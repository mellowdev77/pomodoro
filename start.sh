#!/bin/bash

if command -v python3 &>/dev/null; then
    python3 src/main.py
elif command -v python &>/dev/null; then
    python src/main.py
else
    echo "Please install python before lauching the application."
    exit 1
fi
