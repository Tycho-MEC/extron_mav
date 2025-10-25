"""Extron MAV client for SIS communication."""
import asyncio
import logging
import re

from .const import RESPONSE_TERMINATOR, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class ExtronClient:
    """Client to communicate with Extron MAV via Telnet."""

    def __init__(self, host: str, port: int = 23, password: str | None = None):
        """Initialize the Extron client."""
        self.host = host
        self.port = port
        self.password = password
        self._reader = None
        self._writer = None
        self._lock = asyncio.Lock()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._connected and self._writer is not None

    async def connect(self):
        """Connect to the Extron device."""
        try:
            _LOGGER.info("Connecting to Extron MAV at %s:%s...", self.host, self.port)
            
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=DEFAULT_TIMEOUT
            )
            
            # Read copyright message
            await self._read_until_prompt()
            
            # Handle password if needed
            response = await self._read_response()
            if "Password:" in response:
                if not self.password:
                    _LOGGER.error("Extron MAV requires password but none provided")
                    raise Exception("Password required but not provided")
                
                _LOGGER.debug("Authenticating with password...")
                await self._send_command_raw(self.password)
                login_response = await self._read_response()
                
                if "Login" not in login_response:
                    _LOGGER.error("Authentication failed - invalid password")
                    raise Exception("Invalid password")
                
                _LOGGER.info("Successfully authenticated to Extron MAV")
            
            self._connected = True
            _LOGGER.info("Successfully connected to Extron MAV at %s:%s", self.host, self.port)
            
        except asyncio.TimeoutError:
            _LOGGER.error("Connection timeout to Extron MAV at %s:%s", self.host, self.port)
            raise Exception(f"Timeout connecting to {self.host}:{self.port}")
        except Exception as err:
            _LOGGER.error("Failed to connect to Extron MAV at %s:%s - %s", self.host, self.port, err)
            self._connected = False
            raise Exception(f"Failed to connect: {err}")

    async def disconnect(self):
        """Disconnect from the Extron device."""
        if self._writer:
            _LOGGER.info("Disconnecting from Extron MAV at %s:%s", self.host, self.port)
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.warning("Error during disconnect: %s", err)
            finally:
                self._reader = None
                self._writer = None
                self._connected = False
                _LOGGER.info("Disconnected from Extron MAV at %s:%s", self.host, self.port)

    async def _ensure_connected(self):
        """Ensure we have an active connection, reconnect if needed."""
        if not self.is_connected:
            _LOGGER.warning("Connection lost to Extron MAV, attempting to reconnect...")
            try:
                await self.connect()
            except Exception as err:
                _LOGGER.error("Reconnection failed: %s", err)
                raise

    async def _read_until_prompt(self, timeout: float = DEFAULT_TIMEOUT):
        """Read until we get a complete response."""
        try:
            if not self._reader:
                raise Exception("Not connected - no reader available")
            
            data = await asyncio.wait_for(
                self._reader.readuntil(RESPONSE_TERMINATOR),
                timeout=timeout
            )
            return data.decode('ascii', errors='ignore').strip()
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout reading from Extron MAV at %s:%s", self.host, self.port)
            return ""
        except Exception as err:
            _LOGGER.error("Error reading from Extron MAV: %s", err)
            self._connected = False
            raise

    async def _read_response(self, timeout: float = DEFAULT_TIMEOUT):
        """Read a single response from the device, skipping any extra lines."""
        response = await self._read_until_prompt(timeout)
        
        # Sometimes we get timestamps or other messages before the actual response
        # Keep reading until we get a meaningful response (not a timestamp)
        retry_count = 0
        while response and "," in response and "202" in response and retry_count < 3:
            # Looks like a timestamp, read next line
            _LOGGER.debug("Skipping timestamp line: %s", response)
            response = await self._read_until_prompt(timeout)
            retry_count += 1
        
        return response

    async def _send_command_raw(self, command: str):
        """Send a raw command without reading response (used for password)."""
        if not self._writer:
            raise Exception("Not connected")
        
        self._writer.write(f"{command}\r\n".encode('ascii'))
        await self._writer.drain()

    async def _send_command(self, command: str, expect_response: bool = True):
        """Send a command to the Extron device with auto-reconnect."""
        async with self._lock:
            # Ensure we're connected
            await self._ensure_connected()
            
            try:
                _LOGGER.debug("Sending command to Extron MAV: %s", command)
                self._writer.write(f"{command}\r\n".encode('ascii'))
                await self._writer.drain()
                
                if expect_response:
                    response = await self._read_response()
                    _LOGGER.debug("Received response from Extron MAV: %s", response)
                    
                    # Check for error responses
                    if response.startswith("E"):
                        _LOGGER.warning("Extron MAV returned error: %s", response)
                    
                    return response
                return None
                
            except Exception as err:
                _LOGGER.error("Error sending command to Extron MAV: %s", err)
                self._connected = False
                raise

    async def get_info(self):
        """Get device information."""
        response = await self._send_command("I")
        # Response format: V32X16•A32X16 (example for 32x16 matrix)
        return response

    async def get_output_tie(self, output: int):
        """Get the current input tied to an output (video and audio)."""
        # Command: output# followed by % for video status
        # Response can be either:
        #   - Just a number: "05" (input 5)
        #   - Full format: "Out01 In05 Vid" or "Out01 In05 All"
        response = await self._send_command(f"{output}%")
        
        _LOGGER.debug("Raw tie response for output %s: '%s'", output, response)
        
        # First try to parse full format with "In##"
        match = re.search(r'In(\d+)', response, re.IGNORECASE)
        if match:
            input_num = int(match.group(1))
            _LOGGER.debug("Output %s is tied to input %s", output, input_num)
            return input_num
        
        # If that didn't work, try parsing as just a number
        response = response.strip()
        try:
            input_num = int(response)
            _LOGGER.debug("Output %s is tied to input %s", output, input_num)
            return input_num
        except ValueError:
            _LOGGER.warning("Could not parse tie response for output %s: '%s'", output, response)
            return 0  # Untied

    async def set_output_tie(self, input_num: int, output: int):
        """Tie an input to an output (video and audio)."""
        # Command: input*output!
        # Response: Out##•In##•All
        if input_num == 0:
            # For untie, we would need a different command
            # For now, log a warning - Extron doesn't have a direct "untie" command
            _LOGGER.warning("Cannot untie output %s - Extron MAV requires an input to be tied", output)
            return False
        
        response = await self._send_command(f"{input_num}*{output}!")
        success = "Out" in response and not response.startswith("E")
        
        if success:
            _LOGGER.info("Successfully tied Input %s to Output %s", input_num, output)
        else:
            _LOGGER.error("Failed to tie Input %s to Output %s - response: %s", input_num, output, response)
        
        return success

    async def get_all_ties(self, num_outputs: int):
        """Get all output ties."""
        ties = {}
        for output in range(1, num_outputs + 1):
            try:
                tied_input = await self.get_output_tie(output)
                ties[output] = tied_input
            except Exception as err:
                _LOGGER.error("Error getting tie for output %s: %s", output, err)
                ties[output] = 0
        return ties