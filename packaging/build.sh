#!/usr/bin/env bash
# Build heraldo's Debian package with BeeWare Briefcase and GPG-sign it.
#
#   packaging/build.sh   # -> dist/heraldo_<ver>-1~<distro>-<codename>_<arch>.deb
#                        #    dist/heraldo_<...>.deb.asc  (detached signature)
#
# Needs: briefcase (pip install briefcase), the build packages listed under
# system_requires in pyproject.toml, and gpg. Build on the distro and
# architecture you want to install on (e.g. on the Pi for arm64/armhf).
#
# Environment:
#   BRIEFCASE        briefcase command (default: briefcase)
#   HERALDO_GPG_KEY  key to sign with (default: the key Kurt's commits are
#                    signed with). Set it empty to skip signing. If the key
#                    isn't in the keyring the package is left unsigned.
set -euo pipefail

cd "$(dirname "$0")/.."
BRIEFCASE="${BRIEFCASE:-briefcase}"
GPG_KEY="${HERALDO_GPG_KEY-89B143E859D3984EC0F6FA6B25CCC638FFF4F016}"

# Version: prefer the git tag (v1.2.3 -> 1.2.3), fall back to pyproject.toml.
version="$(git describe --tags --match 'v[0-9]*' 2>/dev/null | sed 's/^v//; s/-\([0-9]*\)-g/+\1.g/')" || true
if [ -z "${version}" ]; then
  version="$(sed -n 's/^version *= *"\(.*\)"/\1/p' pyproject.toml | head -1)"
fi

rm -rf build dist
${BRIEFCASE} package linux system --no-input -C "version=\"${version}\""

for deb in dist/*.deb; do
  if [ -z "${GPG_KEY}" ]; then
    echo "HERALDO_GPG_KEY is empty: ${deb} left unsigned" >&2
  elif gpg --batch --list-secret-keys "${GPG_KEY}" > /dev/null 2>&1; then
    gpg --batch --yes --local-user "${GPG_KEY}" --armor --detach-sign "${deb}"
    gpg --batch --verify "${deb}.asc" "${deb}"
  else
    echo "warning: GPG key ${GPG_KEY} not in keyring: ${deb} left unsigned" >&2
  fi
done

ls -1 dist/*
