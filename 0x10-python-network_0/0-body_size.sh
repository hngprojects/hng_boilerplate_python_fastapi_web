#!/bin/bash
# Script sends a request to a given URL
curl -s "$1" | wc -c
