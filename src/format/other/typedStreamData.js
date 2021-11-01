"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "NeXT TypedStream Data",
	magic : ["NeXT typedstream serialized data", "NeXT/Apple typedstream data"]
};

exports.steps = [() => ({program : "strings"})];
