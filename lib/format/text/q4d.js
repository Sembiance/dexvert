"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "XLD4 Data Document",
	website        : "http://fileformats.archiveteam.org/wiki/XLD4",
	ext            : [".q4d"],
	forbidExtMatch : true,
	magic          : ["XLD4 Data Document"],
	encoding       : "IBM-943",
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
