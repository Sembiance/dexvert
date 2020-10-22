"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Raw Partition",
	magic : [/^DOS\/MBR boot sector/]
};

exports.steps = [() => ({program : "uniso"})];
