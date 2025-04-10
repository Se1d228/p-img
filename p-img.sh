#!/bin/sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QT_QPA_PLATFORM=xcb python3 "$SCRIPT_DIR/p-img.py" "$@"
