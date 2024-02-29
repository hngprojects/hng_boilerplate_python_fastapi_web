#!/bin/bash
# Make a PUT request to 0.0.0.0:5000/catch_me with curl, sending the specified data
curl -sL -X PUT -H "Origin: HolbertonSchool" -d "user_id=98" 0.0.0.0:5000/catch_me
