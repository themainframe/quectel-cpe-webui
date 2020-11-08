# `quectel-cpe-webui`

Supervisor/administration tool for my 5G CPE. I'm using it with the Quectel RM500Q-GL but it may/should work with other Quectel modems, not necessarily just 5G ones.

Features:

* Maintains a `quectel-CM` instance, which in turn maintains the packet data connection & IP setup. Restarts `quectel-CM` if connectivity is lost or it dies.
* Serves a web UI (default on `:8080`) with simple controls and a status display of:
    * Serving cell statistics (including RSSI, RSRP, RSRQ, SINR)
    * Logs from `quectel-CM`
* Allows restarting of `quectel-CM` manually via the web UI

What this _doesn't_ do:

* Configure NAT/routing (use `iptables` to manage this according to your requirements)

## Setup

Before developing or deploying to hardware:

* Install `pip3` dependencies for the application - `pip3 install -r app/requirements.txt`
* Install `npm` dependencies for the web application - `cd app/webserver/static && npm install`
