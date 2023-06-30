# `quectel-onmodem-webui`

This is based on the [quectel-cpe-webui](https://github.com/themainframe/quectel-cpe-webui) published along with an early-generation article on building a 5G modem setup managed by a RPi, published at [5G CPE](https://damow.net/5g-home-broadband).

I am working to modify it to run on the modem itself, to add a simple UI to modems that are directly connected to a PCIe ethernet module, as desribed at my repo [Quectel RGMII Configuration Notes](https://github.com/natecarlson/quectel-rgmii-configuration-notes).

## Current status

* Code referencing Quectel_CM has been commented out.
* The app runs, pulls info from the modem with AT commands, and displays it.

### Working Features

* Serves a web UI (default on `:8080`) with simple controls and a status display of:
  * Serving cell statistics (including RSSI, RSRP, RSRQ, SINR) (which can also be sent to a `statsd` instance, if one can be accessed from the modem, either via port forward on the device behind it, or an internet isntance.)

### Planned features

* Run on the modem itself
  * Will need a custom Python build to run on the modem's OS.
  * Will also require figuring out how to properly interface with the modem via the /dev/smd interface.
* If the connection goes down, restart the connection through either AT commands or QMAP or something else.
* Expose an AT console through the web interface.

"Stretch goal" features:

* Authentication for features that can modify anything
* Allow configuration of the modem through the web interface
  * APN
  * Port forwarding
  * Cell locking
* Local logging of signal status, with a nice interface to see trends over time
* Prometheus exporter, so that it can be polled from the module instead of pushed out.
* TLS (probably self-signed)
* Add firewall rule to block access to the app over the public interface
* Web shell so that user can log in to the adb-style shell without having to be connected via usb.

## Setup

> These instructiosns are basically the original ones included in the app. It will work for setting it up on a system connected to the modem via USB, but will not work when the code is to run directly on the modem.

* Install `pip3` dependencies for the application - `pip3 install -r app/requirements.txt`
* Install `npm` dependencies for the web application - `cd app/webserver/static && npm install`
* Copy `config.yml.dist` to `app/config.yml` and make changes as appropriate to your installation. Particularly the AT interface device file, APN details etc.

You can set the service up as a `systemd` service by adding `/lib/systemd/system/quectel-cpe-webui.service`:

    [Unit]
    Description=Quectel CPE Web UI
    After=network.target

    [Service]
    User=pi
    WorkingDirectory=/home/pi/quectel-cpe-webui/
    ExecStart=/usr/bin/python3 /home/pi/quectel-cpe-webui/app/main.py
    Restart=always
    TimeoutStartSec=10
    RestartSec=10

    [Install]
    WantedBy=network.target

Then enable and start the service with:

```bash
sudo systemctl enable quectel-cpe-webui.service
sudo systemctl start quectel-cpe-webui.service
```
