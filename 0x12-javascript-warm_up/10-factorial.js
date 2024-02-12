#!/usr/bin/node
const args = process.argv.slice(2);
function factorial (arg) {
  if (arg === 1) {
    return (1);
  } else {
    return (factorial(arg - 1) * arg);
  }
}
let ar;
if (!isNaN(args[0])) {
  ar = parseInt(args[0]);
} else {
  ar = 1;
}
console.log(factorial(ar));
