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

`packaging/build.sh` builds a Debian package with [BeeWare Briefcase](https://briefcase.readthedocs.io/) (`briefcase package linux system`). dbus-python and PyGObject are compiled into the package, so it only needs the distro's Python, BlueZ and the GLib/D-Bus libraries at runtime:

```bash
sudo apt install bluez libcairo2-dev libdbus-1-dev libgirepository1.0-dev libglib2.0-dev pkg-config
pip install briefcase
packaging/build.sh
# dist/heraldo_<version>-1~<distro>-<codename>_<arch>.deb
# dist/heraldo_<version>-1~<distro>-<codename>_<arch>.deb.asc
sudo apt install ./dist/heraldo_*.deb
```

The version comes from the latest `v*` git tag, falling back to `pyproject.toml`. Build on the distro and architecture you want to install on (e.g. on the Pi for `arm64`/`armhf`).

The `.deb` gets a detached GPG signature (`.deb.asc`) from key `89B143E859D3984EC0F6FA6B25CCC638FFF4F016` when that key is in your keyring; set `HERALDO_GPG_KEY` to sign with another key, or to an empty value to skip signing. Verify with:

```bash
gpg --verify heraldo_*.deb.asc heraldo_*.deb
```
