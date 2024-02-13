#!/usr/bin/node
const List = require('./100-data').list;
const newList = List.map((value, index) => value * index);

console.log(List);
console.log(newList);
