#!/usr/bin/env bash
# Build the signed ble-beacon Debian package: a systemd service that runs
# heraldo as a BLE beacon. It depends on the heraldo package
# (packaging/build.sh) and contains no code of its own, so it's
# architecture-independent (Architecture: all).
#
#   packaging/build-beacon.sh   # -> dist/ble-beacon_<ver>-1_all.deb
#
# Needs: dpkg-deb and debsigs. Like build.sh it needs a GPG secret key to sign
# the package and fails without one.
#
# Environment:
#   HERALDO_GPG_KEY  key to sign with (default: the first GPG secret key)
set -euo pipefail

cd "$(dirname "$0")/.."
SRC=packaging/ble-beacon
GPG_KEY="${HERALDO_GPG_KEY:-$(gpg --batch --with-colons --list-secret-keys 2>/dev/null | awk -F: '$1 == "fpr" { print $10; exit }')}"

if [ -z "${GPG_KEY}" ] || ! gpg --batch --list-secret-keys "${GPG_KEY}" >/dev/null 2>&1; then
  echo "error: no GPG secret key${GPG_KEY:+ ${GPG_KEY}} found; one is needed to sign the package" >&2
  exit 1
fi

# Same version as heraldo: [project].version in pyproject.toml.
VERSION="$(python3 -c 'import re, sys; print(re.search(r"^version\s*=\s*\"([^\"]+)\"", open("pyproject.toml").read(), re.M).group(1))')"
DEB_VERSION="${VERSION}-1"

STAGE="build/ble-beacon"
rm -rf "${STAGE}"
install -d "${STAGE}/DEBIAN" "${STAGE}/etc/default" "${STAGE}/usr/lib/systemd/system" \
  "${STAGE}/usr/share/doc/ble-beacon"
install -m 0644 "${SRC}/ble-beacon.service" "${STAGE}/usr/lib/systemd/system/ble-beacon.service"
install -m 0644 "${SRC}/default" "${STAGE}/etc/default/ble-beacon"
install -m 0644 LICENSE "${STAGE}/usr/share/doc/ble-beacon/copyright"
install -m 0755 "${SRC}/postinst" "${SRC}/prerm" "${SRC}/postrm" "${STAGE}/DEBIAN/"
echo /etc/default/ble-beacon > "${STAGE}/DEBIAN/conffiles"
cat > "${STAGE}/DEBIAN/control" <<CONTROL
Package: ble-beacon
Version: ${DEB_VERSION}
Architecture: all
Maintainer: Kurt Sell <kurt.sell8@gmail.com>
Depends: heraldo (>= ${VERSION}), bluez, systemd
Section: net
Priority: optional
Homepage: https://github.com/ksell8/heraldo
Description: BLE beacon service using heraldo
 Runs heraldo as the ble-beacon systemd service, started at boot. Set the
 beacon (heraldo's command-line arguments) in /etc/default/ble-beacon.
CONTROL

# xz, not zstd: debsigs 0.1.26 can't sign zstd members (see build.sh).
mkdir -p dist
OUT="dist/ble-beacon_${DEB_VERSION}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "${STAGE}" "${OUT}"
debsigs --sign=origin -k "${GPG_KEY}" "${OUT}"

ls -1 "${OUT}"
