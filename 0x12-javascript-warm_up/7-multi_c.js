#!/usr/bin/node
const args = process.argv.slice(2);
const num = parseInt(args[0]);
if (!isNaN(num)) {
  for (let i = 0; i < num; i++) {
    console.log('C is fun');
  }
} else {
  console.log('Missing number of occurrences');
}
