"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "The Sterling COMPressor archive",
	website : "http://fileformats.archiveteam.org/wiki/TSComp",
	magic   : ["TSComp compressed data", "TSComp archive data"]
};

exports.converterPriorty = ["tscomp"];
