#!/usr/bin/node
const fs = require('fs');

const filePath = process.argv[2];

if (filePath) {
  fs.readFile(filePath, 'utf-8', (err, data) => {
    if (err) {
      console.error(err);
    } else {
      console.log(data.toString());
    }
  });
} else {
  process.exit(1);
}
