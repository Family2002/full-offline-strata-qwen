#!/bin/sh
# Join split release pieces back into one file and check SHA-256.
# Usage: sh reassemble.sh Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
# The pieces are <name>.part-00, part-01, ... in the current directory.
# The expected hash is the first field of the matching line in SHA256SUMS.txt.
set -eu
name=${1:?file name, without .part-NN}
parts=$(ls "$name".part-* 2>/dev/null | sort) || true
if [ -z "$parts" ]; then
  echo "no pieces named $name.part-*" >&2
  exit 1
fi
cat $parts > "$name"
if [ -f SHA256SUMS.txt ]; then
  want=$(awk -v n="$name" '$2 == n { print $1; exit }' SHA256SUMS.txt)
  got=$(sha256sum "$name" | awk '{ print $1 }')
  if [ -n "$want" ] && [ "$got" != "$want" ]; then
    echo "hash $got != $want" >&2
    exit 1
  fi
  echo "ok $got"
else
  sha256sum "$name"
fi
