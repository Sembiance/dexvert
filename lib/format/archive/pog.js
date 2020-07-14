"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Print Shop Graphic POG Archive",
	website : "http://fileformats.archiveteam.org/wiki/The_Print_Shop",
	ext     : [".pog"],
	magic   : ["The Print Shop graphic"]
};

exports.steps = [() => ({program : "deark"})];
