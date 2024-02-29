#!/bin/bash
#Script displays all HTTPS methds a server will accept
curl -Is "$1" | grep -i "^allow:" | sed 's/Allow: //i'
