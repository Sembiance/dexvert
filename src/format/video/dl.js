"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name    : "DL Video",
	website : "http://fileformats.archiveteam.org/wiki/DL",
	ext     : [".dl"]
};

// dl files will start with 0x03, 0x02 or 0x01
exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, [Buffer.from([0x03]), Buffer.from([0x02]), Buffer.from([0x01])]);

exports.converterPriority = ["xanim", {program : "deark", flags : {dearkModule : "dlmaker", dearkJoinFrames : true}}];
