# HATool

Simple CLI tool for querying the Home Assistant API. More of an example than anything at this point.

Uses the DBus secret service through GLib introspection.

## Requirements

`sudo apt install libsecret-1-dev python3-gi gir1.2-secret-1`


## Using

 - Rename `power1.json.dist` as `power1.json`.
 - Put hostname in power1.json.
 - Follow instructions from `./power1.py -h`.

