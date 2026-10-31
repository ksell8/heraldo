# heraldo

BLE beacon advertiser for Raspberry Pi. Requires Linux with BlueZ — the necessary system packages (`python3-dbus`, `python3-gi`) come pre-installed on Raspberry Pi OS.

## Installation

### With pip

Raspberry Pi OS ships with the required bindings (`python3-dbus`, `python3-gi`) pre-installed system-wide. Use `--no-deps` so pip doesn't try to rebuild them from PyPI:

```bash
pip install --no-deps .
```

If you're on a machine that doesn't already have the bindings, install them first:

```bash
sudo apt install python3-dbus python3-gi
```

### Without pip

Clone the repo, then create `/usr/local/bin/heraldo`:

```bash
#!/bin/bash
PYTHONPATH=/path/to/heraldo exec python3 -m heraldo "$@"
```

```bash
sudo chmod +x /usr/local/bin/heraldo
```

## Usage

```bash
heraldo ibeacon \
  --uuid 550e8400-e29b-41d4-a716-446655440000 \
  --major 1 \
  --minor 1
```

Runs until Ctrl+C or SIGTERM, then unregisters cleanly from BlueZ.

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--uuid` | yes | — | Beacon UUID |
| `--major` | yes | — | Major value (0–65535) |
| `--minor` | yes | — | Minor value (0–65535) |
| `--tx-power` | no | `-59` | TX power in dBm (calibrate to RSSI at 1 m) |
| `--name` | no | — | Bluetooth adapter alias shown to scanners |
| `--adapter` | no | auto | DBus adapter path (e.g. `/org/bluez/hci1`) |
| `--ad-type` | no | `peripheral` | `peripheral` or `broadcast` |

## Packaging

`packaging/build.sh` builds a Debian package with [BeeWare Briefcase](https://briefcase.readthedocs.io/) (`briefcase package linux system`) and signs it with GPG.

Briefcase installs dbus-python and PyGObject into the package itself, but it builds them from source, so the build machine needs their C headers. Briefcase checks for these packages (`system_requires` in `pyproject.toml`) but doesn't install them:

```bash
sudo apt install bluez libcairo2-dev libdbus-1-dev libgirepository1.0-dev libglib2.0-dev pkg-config
pip install briefcase
packaging/build.sh
# dist/heraldo_<version>-1~<distro>-<codename>_<arch>.deb
# dist/heraldo_<version>-1~<distro>-<codename>_<arch>.deb.asc
```

Machines that install the `.deb` don't need any of that: `sudo apt install ./heraldo_*.deb` pulls in the runtime dependencies (`bluez` and the GLib/D-Bus libraries) itself.

The version comes from `version` in `pyproject.toml`. Build on the distro and architecture you want to install on (e.g. on the Pi for `arm64`/`armhf`).

A GPG secret key is needed to do the build: the `.deb` gets a detached signature (`.deb.asc`) made with your default key, or the one named in `HERALDO_GPG_KEY`. Verify with:

```bash
gpg --verify heraldo_*.deb.asc heraldo_*.deb
```
