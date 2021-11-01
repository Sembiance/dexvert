"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name           : "Macromedia Flash Compiled EXE",
	website        : "http://fileformats.archiveteam.org/wiki/SWF",
	ext            : [".exe"],
	forbidExtMatch : true,
	magic          : ["Macromedia Projector/Flash executable"]
};

exports.converterPriority =
[
	["EXE2SWFExtractor", {program : "dexvert", flags : {deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.swf`), state.output.absolute])}]
];
