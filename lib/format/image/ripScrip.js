"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Remote Imaging Protocol Script",
	website     : "http://fileformats.archiveteam.org/wiki/RIPscrip",
	ext         : [".rip"],
	magic       : ["RIPscript"],
	unsupported : true,
	notes       : XU.trim`
		A vector based format. Would love to convert to SVG. This project started support for that: https://github.com/cgorringe/RIPtermJS
		I could extend that project to make a true ripscrip-to-svg node based converter.
		Other tools: http://archives.thebbs.org/ra109a.htm`
};

exports.converterPriorty = ["deark", "ansilove", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
