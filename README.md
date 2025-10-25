<a id="readme-top"></a>

<!-- PROJECT LOGO 
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->
<h3 align="center">Extron MAV Plus for Home Assistant</h3>

  <p align="center">
    Remote control of Extron MAV Plus matrices from Home Assistant
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#compatability">Compatability</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT -->
## About

The custom component provides an integration for Home Assistant to remote control Extron MAV Plus matrices.  The integration uses Extron's Simple Instruction Set to read the status and control the matrix over a Telnet connection.

The integration currently supports simple switching of inputs to outputs.  Each output is exposed as an entity in Home Assistant allowing them to be targetted by button presses, automations and scenes.

<!-- GETTING STARTED -->
## Getting Started

### Compatability

This integration should work with all Extron MAV Plus and Crosspoint 400 matrices.  It may potentially work with other Extron matrices that implement Extron Simple Instruction Set over Telnet.

The integration has been tested and proven to work with the following devices:
* MAV Plus 1616 SVA

### Installation

To install the integration:

1. Clone the repository
2. Copy the extron_mav folder to the custom_components folder in your Home Assistant installation
3. Restart Home Assistant

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

To add a new matrix to Home Assistant:

1. Go to "Settings" -> "Devices & services" to open the Integrations page, and then select "Add integration".
2. If the integration has been sucessfully installed "Extron MAV Matrix" will be available in the list.
3. Add the following details:
* host (required) - the hostname or IP address of the matrix
* port (required) - the port to use for the telnet connection, set to 23 by default
* password (optional) - the password for the matrix, leave blank for none.
* num_inputs - the number of inputs on the matrix
* num_outputs - the number of outputs on the matrix
4. Click submit.

The matrix will be added to Home Assistant as a device with a separate entity for each output.  The currently routed input can be changed from a drop down list.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

Planned features:

- [ ] Device type identifcation
- [ ] Device health monitoring
- [ ] Volume control
    - [ ] Switching audio inputs between +4/-10
    - [ ] Adjustable output gain
- [ ] Separate switching of audio and video levels
- [ ] Custom input and output names

See the [open issues](https://github.com/Tycho-MEC/extron_mav/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/github_username/repo_name/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=github_username/repo_name" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgements

Thanks to:

* Home Assistant for the incredible open source platform. [https://www.home-assistant.io/](https://www.home-assistant.io/)
* The Best Readme Template. [https://github.com/othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
