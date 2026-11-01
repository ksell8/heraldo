# Changelog

## Unreleased

- New `ble-beacon` package (`packaging/build-beacon.sh`): runs heraldo as the `ble-beacon` systemd service, configured in `/etc/default/ble-beacon`. Moved here from La Semilla's Ansible `bluetooth` role.

## 1.0.0

- No functional changes.
- Packaged as a Debian package built with Briefcase (`packaging/build.sh`), GPG-signed with debsigs.

## 0.1.0

- Initial prototype, made for the La Semilla art presentation (art class final project): iBeacon and Eddystone advertising through BlueZ.
