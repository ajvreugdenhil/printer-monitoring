# printer-monitoring

**NOTE: this is not a safety system!**

This project was designed to assist 3d printer operators with managing their printers. One important aspect is partial autonomy. The service evaluates printer parameters and determines if they're within normal range. If they veer outside, logs are created and the indicators are adjusted accordingly.

## Indicators

solid red - cannot print
blinking orange - connection issues
solid orange - parameters not ideal
blinking green - warming up
solid green - operational
blinking white - cooling down
solid white - idle
