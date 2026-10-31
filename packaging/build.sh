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
# A GPG secret key is needed to sign the package; the build fails without one.
#
# Environment:
#   BRIEFCASE        briefcase command (default: briefcase)
#   HERALDO_GPG_KEY  key to sign with (default: gpg's default secret key)
set -euo pipefail

cd "$(dirname "$0")/.."
BRIEFCASE="${BRIEFCASE:-briefcase}"
GPG_KEY="${HERALDO_GPG_KEY:-}"

# Check for the signing key before spending time on the build.
if ! gpg --batch --list-secret-keys ${GPG_KEY:+"${GPG_KEY}"} 2>/dev/null | grep -q '^sec'; then
  echo "error: no GPG secret key${GPG_KEY:+ ${GPG_KEY}} found; one is needed to sign the package" >&2
  exit 1
fi

# The version comes from [project].version in pyproject.toml.
rm -rf build dist
${BRIEFCASE} package linux system --no-input

for deb in dist/*.deb; do
  gpg --batch --yes ${GPG_KEY:+--local-user "${GPG_KEY}"} --armor --detach-sign "${deb}"
  gpg --batch --verify "${deb}.asc" "${deb}"
done

ls -1 dist/*
