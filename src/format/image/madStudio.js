"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Mad Studio",
	website       : "http://fileformats.archiveteam.org/wiki/Mad_Studio",
	ext           : [".gr1", ".gr2", ".gr3", ".gr0", ".mpl", ".msl", ".spr", ".an2", ".an4", ".an5", ".tl4"],
	untrustworthy : true
};

exports.converterPriority = ["recoil2png"];
