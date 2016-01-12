#!/bin/bash
# This file exists for backwards compatibility with older versions of Jasper.
# It might be removed in future versions.
aplay -D plughw:1,0 -c2 -r48000 -fS16_LE < /dev/zero &
"${0%/*}/../jasper.py"
