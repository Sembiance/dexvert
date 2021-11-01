"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ColoRIX",
	website        : "http://fileformats.archiveteam.org/wiki/ColoRIX",
	ext            : [".rix", ".sca", ".scb", ".scc", ".sce", ".scf", ".scg", ".sci", ".sck", ".scl", ".scn", ".sco", ".scp", ".scq", ".scr", ".sct", ".scu", ".scv", ".scw", ".scx", ".scy", ".scz"],
	magic          : ["ColoRIX bitmap"],
	forbiddenMagic : require("../executable/windowsSCR.js").meta.magic	// Never want to convert windows SCR files as an image
};

exports.converterPriority = ["nconvert"];
