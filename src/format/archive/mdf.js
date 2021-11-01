"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require("../../C.js");

exports.meta =
{
	name      : "Alcohol 120% MDF Image",
	website   : "http://fileformats.archiveteam.org/wiki/MDF_and_MDS",
	ext       : [".mdf"],
	magic     : ["ISO 9660 CD image"],
	weakMagic : true,
	priority  : C.PRIORITY.TOP // Due to generic ISO magic, needs to be higher priority
};

exports.converterPriority =
[
	["MDFtoISO", {program : "dexvert", flags : {deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.iso`), state.output.absolute])}],
	"IsoBuster"
];
