# printer-monitoring

**NOTE: this is not a safety system!**

**NOTE: this project is pre-alpha. Use at own risk!**

This project was designed to assist 3d printer operators with managing their printers. By leveraging the position of additive manufacturing equipment on the cloud edge, we can build an optimized error detection flow, with a safe internet connected engineering workflow as secondary objective.

## System description

The system consists of multiple parts, shown in the following diagram.

![Overview of the entire system, consisting of hardware, RPi and cloud sections](docs/system-overview.png "system overview")

The green blocks represent the custom hardware and necessary software that is added to the printer. These can function without direct user interaction by querying data from OctoPrint. They are directly useful to the operator in the machines physical vicinity.

The blue blocks are responsible for providing the operator with detailed metrics and logs regarding the health of the equipment.

## Quick start

Set up a Raspberry Pi with Octoprint and Netdata.

To set up the project, flash the MCU and connect its peripherals. Connect it to the Pi.

Set up Docker and Docker-compose on the Pi. Upload the relevant docker-compose including the Status Gateway, and Prometheus. Make a .env file with the desired settings.

Test the system. Currently this has to be done manually.

## Stack light

The stack light provides the operator with data regarding the system state. The meaning of the different colors and patterns is as follows.

| color  | behaviour | meaning             |
| ------ | --------- | ------------------- |
| red    | solid     | error               |
| orange | blinking  | connectivity issues |
| orange | solid     | not ready           |
| green  | blinking  | warming up          |
| green  | solid     | printing            |
| white  | blinking  | waiting             |
| white  | solid     | idle                |
