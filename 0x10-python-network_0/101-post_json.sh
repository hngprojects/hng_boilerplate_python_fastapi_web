#!/bin/bash
# Sends a JSON POST request a URL
curl -s -H "Content-Type: application/json" -d "$(cat "$2")" "$1"
