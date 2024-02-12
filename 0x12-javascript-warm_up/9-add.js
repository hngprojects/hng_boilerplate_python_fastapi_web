#!/usr/bin/node
const args = process.argv.slice(2);
function add (a, b) {
  if ((!isNaN(a)) && (!isNaN(b))) {
    a = parseInt(a);
    b = parseInt(b);
    console.log(a + b);
  } else {
    console.log('NaN');
  }
}
add(args[0], args[1]);
