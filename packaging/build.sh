#!/usr/bin/env bash
# Build heraldo as a self-contained executable (PyInstaller, bundled Python
# runtime) and wrap it in a Debian package.
#
#   packaging/build.sh            # -> dist/heraldo-<ver>-linux-<arch>.tar.gz
#                                 #    dist/heraldo_<ver>_<debarch>.deb
#
# Needs: python3 with dbus-python + PyGObject importable (on Debian/Raspberry
# Pi OS: apt install python3-dbus python3-gi), pyinstaller, dpkg-deb.
# Set PYTHON to pick the interpreter (default: python3).
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3}"

# Version: prefer the git tag (v1.2.3 -> 1.2.3), fall back to pyproject.toml.
version="$(git describe --tags --match 'v[0-9]*' 2>/dev/null | sed 's/^v//; s/-\([0-9]*\)-g/+\1.g/')" || true
if [ -z "${version}" ]; then
  version="$(sed -n 's/^version *= *"\(.*\)"/\1/p' pyproject.toml | head -1)"
fi

arch="$(uname -m)"
debarch="$(dpkg --print-architecture 2>/dev/null || echo "${arch}")"

rm -rf build dist
"${PYTHON}" -m PyInstaller --noconfirm --clean \
  --name heraldo --specpath build \
  --collect-submodules heraldo \
  --hidden-import gi.repository.GLib \
  heraldo/__main__.py

./dist/heraldo/heraldo --help > /dev/null

# Portable tarball of the PyInstaller bundle.
tarname="heraldo-${version}-linux-${arch}"
tar -C dist -czf "dist/${tarname}.tar.gz" --transform "s,^heraldo,${tarname}," heraldo

# Debian package: bundle in /usr/lib/heraldo, command in /usr/bin.
pkgroot="build/deb"
mkdir -p "${pkgroot}/DEBIAN" "${pkgroot}/usr/lib" "${pkgroot}/usr/bin"
cp -a dist/heraldo "${pkgroot}/usr/lib/heraldo"
ln -s ../lib/heraldo/heraldo "${pkgroot}/usr/bin/heraldo"
sed -e "s/@VERSION@/${version}/" -e "s/@ARCH@/${debarch}/" \
  packaging/debian/control.in > "${pkgroot}/DEBIAN/control"
echo "Installed-Size: $(du -sk "${pkgroot}/usr" | cut -f1)" >> "${pkgroot}/DEBIAN/control"
dpkg-deb --root-owner-group --build "${pkgroot}" "dist/heraldo_${version}_${debarch}.deb"

ls -1 dist/*.tar.gz dist/*.deb
