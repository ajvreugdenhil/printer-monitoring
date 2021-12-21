# printer-monitoring

NOTE: this is not a safety system

This project was designed to assist 3d printer operators with managing their printers. By leveraging the position of additive manufacturing equipment on the cloud edge, we can build an optimized error detection flow, with a safe internet connected engineering workflow as secondary objective.

## System description

The system consists of multiple parts, shown in the following diagram.

![Overview of the entire system, consisting of hardware, RPi and cloud sections](docs/system-overview.png "system overview")

The green blocks represent the custom hardware and necessary software that is added to the printer. These can function without direct user interaction by querying data from OctoPrint. They are directly useful to the operator in the machines physical vicinity.

The blue blocks are responsible for providing the operator with detailed metrics regarding the health of the equipment.

## Quick start

For an introduction on how to set up each of the three major subsystems, see the readmes of the [status gateway](status-gateway/README.md), [printer module](printer-module/README.md) and the [example cloud](cloud/README.md).

The cloud is not essential for the printer module to function, but the status gateway is. Setting the system up with only the cloud and parts of the gateway is also possible, of course. But because that is fairly trivial, it is not explicitly supported by this project.

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

## Roadmap

There are no concrete plans to further develop this system. However, if it is further developed, the following points will require consideration.

- Expand logging and add logs to the dashboard.
- Publish STL files for mounting the hardware to the machine.
- Add blue or replace white with blue in the stack light.
- Restructure metric names to be more consistent.
- Secret management is not ideal, especially in status-gateway. This cannot be fully solved but it can be improved.
