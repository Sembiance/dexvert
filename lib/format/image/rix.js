"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ColoRIX",
	website  : "http://fileformats.archiveteam.org/wiki/ColoRIX",
	ext      : [".rix", ".sca", ".scb", ".scc", ".sce", ".scf", ".scg", ".sci", ".sck", ".scl", ".scn", ".sco", ".scp", ".scq", ".scr", ".sct", ".scu", ".scv", ".scw", ".scx", ".scy", ".scz"],
	magic    : ["ColoRIX bitmap"]
};

exports.converterPriorty = ["nconvert"];
