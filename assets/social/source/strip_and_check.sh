#!/usr/bin/env bash
# Usage: strip_and_check.sh img1 [img2 ...]  — strips ALL metadata, then fails if any XMP/IPTC/EXIF/C2PA/JUMBF remains.
set -u; rc=0
for f in "$@"; do
  exiftool -q -overwrite_original -all= "$f" || { echo "FAIL strip $f"; rc=1; continue; }
  hits=$(exiftool -a -G1 "$f" | grep -iE '^\[(XMP[^]]*|IPTC|EXIF|IFD[0-9]*|JUMBF|C2PA|CBOR|Photoshop|ICC_Profile)\]' ; strings "$f" | grep -iE 'c2pa|jumb|trainedAlgorithmic|digitalsourcetype' )
  if [ -n "$hits" ]; then echo "FAIL $f"; echo "$hits"; rc=1; else echo "PASS $f (no XMP/IPTC/EXIF/C2PA/JUMBF)"; fi
done; exit $rc
