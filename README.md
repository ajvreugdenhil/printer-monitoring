# printer-monitoring

**NOTE: this is not a safety system!**

This project was designed to assist 3d printer operators with managing their printers. One important aspect is partial autonomy. The service evaluates printer parameters and determines if they're within normal range. If they veer outside, logs are created and the indicators are adjusted accordingly.

## System description

![Overview of the entire system, consisting of hardware, RPi and cloud sections](docs/system-overview.png "system overview")

## Indicators

| color  | behaviour | meaning             |
| ------ | --------- | ------------------- |
| red    | solid     | error               |
| orange | blinking  | connectivity issues |
| orange | solid     | not ready           |
| green  | blinking  | warming up          |
| green  | solid     | printing            |
| white  | blinking  | waiting             |
| white  | solid     | idle                |
