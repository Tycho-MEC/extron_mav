"""Constants for the Extron MAV integration."""

DOMAIN = "extron_mav"

# Configuration
CONF_NUM_INPUTS = "num_inputs"
CONF_NUM_OUTPUTS = "num_outputs"

# Defaults
DEFAULT_PORT = 23
DEFAULT_TIMEOUT = 5
UPDATE_INTERVAL = 30  # seconds

# Response terminators
RESPONSE_TERMINATOR = b"\r\n"