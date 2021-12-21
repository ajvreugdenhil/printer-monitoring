# printer-monitoring: status-gw

The status gateway was designed to be as simple as possible to set up. It has been tested on a raspberry pi 3b+ with raspberry OS Lite.

Setting up requires the following steps.

- Install Octoprint
- Install Docker and Docker-compose
- Install Netdata (optional, may be replaced later)
- Install the Octoprint prometheus_export plugin
- make the following configuration changes:

- in `/etc/avahi/avahi-daemon.conf`, uncomment the following line:

```ini
allow-interfaces=eth0, wlan0
```

- Restart avahi with `sudo service avahi-daemon restart`

- in `.octoprint/config.yaml`, uncomment the interfaces line and make sure the relevant interfaces are listed. (Likely eth0 and/or wlan0). See the [documentation](https://docs.octoprint.org/en/master/bundledplugins/discovery.html) for more information.

To check if mDNS is working, execute `avahi-browse -ar` on your own machine. Avahi may cache data. To see this cache, run `avahi-browse -a -c`. To clear the cache, run `sudo avahi-daemon --kill`.

- Clone the repository or copy the status-gateway folder to it. `cd` into it.
- Run `cp env-example .env`
- Make the following mandatory changes
  - in .env, set the printer token with one from Octoprint
  - in prometheus.yml, set the printer token with one from Octoprint
  - in telegraf.conf, set all the influxdb variables

- Run with `sudo docker-compose up --build` or `sudo docker-compose up --build -d`
