"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Atari ATR Floppy Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/ATR",
	ext     : [".atr"],
	magic   : ["Atari ATR disk image"]
};

exports.steps = [() => ({program : "deark"})];
