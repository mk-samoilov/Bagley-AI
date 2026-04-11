#!/bin/bash
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
chmod +x "$SCRIPT_DIR/bagley.sh"
sudo ln -sf "$SCRIPT_DIR/bagley.sh" /usr/local/bin/bagley
