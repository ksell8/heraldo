#!/usr/bin/env bash
# Build heraldo's signed Debian package with BeeWare Briefcase.
#
#   packaging/build.sh   # -> dist/heraldo_<ver>-1~<distro>-<codename>_<arch>.deb
#
# Needs: Python 3.11+, briefcase >= 0.4.7 (pip install "briefcase>=0.4.7"),
# debsigs, and the build packages listed under system_requires in
# pyproject.toml. Build on the distro and architecture you want to install on
# (e.g. on the Pi for arm64/armhf).
#
# A GPG secret key is needed to sign the package; the build fails without one.
# Briefcase embeds the signature in the .deb with debsigs.
#
# Environment:
#   BRIEFCASE        briefcase command (default: briefcase)
#   HERALDO_GPG_KEY  key to sign with (default: the first GPG secret key)
set -euo pipefail

cd "$(dirname "$0")/.."
BRIEFCASE="${BRIEFCASE:-briefcase}"
GPG_KEY="${HERALDO_GPG_KEY:-$(gpg --batch --with-colons --list-secret-keys 2>/dev/null | awk -F: '$1 == "fpr" { print $10; exit }')}"

# Check for the signing key before spending time on the build.
if [ -z "${GPG_KEY}" ] || ! gpg --batch --list-secret-keys "${GPG_KEY}" >/dev/null 2>&1; then
  echo "error: no GPG secret key${GPG_KEY:+ ${GPG_KEY}} found; one is needed to sign the package" >&2
  exit 1
fi

# debsigs (0.1.26) can't read zstd-compressed members, which Ubuntu's dpkg-deb
# uses by default: it would sign only debian-binary and the signature would
# fail to verify. xz is Debian's default and works.
export DPKG_DEB_COMPRESSOR_TYPE="${DPKG_DEB_COMPRESSOR_TYPE:-xz}"

# The version comes from [project].version in pyproject.toml.
rm -rf build dist
${BRIEFCASE} package linux system --no-input --identity "${GPG_KEY}"

ls -1 dist/*
