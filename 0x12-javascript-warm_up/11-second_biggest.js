#!/usr/bin/node
let parg;
let len;
const args = process.argv.slice(2);
if (args.length === 0 || args.length === 1) {
  console.log(0);
} else {
  parg = args.sort();
  len = args.length;
  console.log(parg[len - 2]);
}
