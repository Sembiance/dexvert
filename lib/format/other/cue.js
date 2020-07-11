"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "ISO CUE Sheet",
	website     : "http://fileformats.archiveteam.org/wiki/CUE_and_BIN",
	ext         : [".cue"],
	magic       : ["ISO CDImage cue", "Cue Sheet"],
	unsupported : true,
	notes       : "CUE files are not handled directly. Instead target the .BIN file and the CUE is automatically found and taken into account."
};
