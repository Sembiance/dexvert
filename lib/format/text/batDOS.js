"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "DOS Batch File",
	website        : "http://fileformats.archiveteam.org/wiki/BAT",
	ext            : [".bat"],
	forbidExtMatch : true,
	magic          : ["DOS batch file"],
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
