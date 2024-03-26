#!/usr/bin/node
const fs = require('fs');

const filePath = process.argv[2];
const contentToWrite = process.argv[3] || '';

if (filePath) {
  fs.writeFile(filePath, contentToWrite, 'utf-8', (err) => {
    if (err) {
      console.error(err);
    }
  });
} else {
  process.exit(1);
}
