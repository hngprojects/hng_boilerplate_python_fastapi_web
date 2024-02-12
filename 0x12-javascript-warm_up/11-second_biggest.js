#!/usr/bin/node
const args = process.argv.slice(2);
if (args.length === 0 || args.length === 1) {
  console.log(0);
} else if (args.length === 2) {
  const a = parseInt(args[0]);
  const b = parseInt(args[1]);
  if (a > b) {
    console.log(b);
  } else {
    console.log(a);
  }
} else {
  let a = parseInt(args[1]);
  let b = parseInt(args[2]);
  let v = parseInt(args[0]);
  for (let k = 0; k < args.length; k++) {
    for (let i = 0; i < args.length - 2; i++) {
      a = parseInt(args[i + 1]);
      b = parseInt(args[i + 2]);
      if ((a >= v) && (b >= v)) {
        if (b > a) {
          v = a;
        } else {
          v = b;
        }
      }
    }
  }
  console.log(v);
}
