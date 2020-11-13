# `quectel-cpe-webui`

Supervisor/administration tool for my [5G CPE](https://damow.net/5g-home-broadband). I'm using it with the Quectel RM500Q-GL but it may/should work with other Quectel modems, not necessarily just 5G ones.

Features:

* Maintains a `quectel-CM` instance, which in turn maintains the packet data connection & IP setup. Restarts `quectel-CM` if connectivity is lost or it dies.
* Serves a web UI (default on `:8080`) with simple controls and a status display of:
    * Serving cell statistics (including RSSI, RSRP, RSRQ, SINR) (which can also be sent to a `statsd` instance)
    * Logs from `quectel-CM`
* Allows restarting of `quectel-CM` manually via the web UI

What this _doesn't_ do:

* Configure NAT/routing (use `iptables` to manage this according to your requirements)

## Setup

* Install `pip3` dependencies for the application - `pip3 install -r app/requirements.txt`
* Install `npm` dependencies for the web application - `cd app/webserver/static && npm install`
* Copy `config.yml.dist` to `app/config.yml` and make changes as appropriate to your installation. Particularly the AT interface device file, APN details etc.
* Install `Quectel_CM` and update the path in `app/config.yml` - this can be obtained from Quectel themselves

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

There's also an installer script (`tools/install.sh`) but I'd only recommend that when starting absolutely from scratch.
