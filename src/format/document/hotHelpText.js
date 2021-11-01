"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "HotHelp Text",
	website        : "http://fileformats.archiveteam.org/wiki/HotHelp",
	ext            : [".txt", ".hdr"],
	forbidExtMatch : true,
	magic          : ["HotHelp Text", "HotHelp Header"],
	unsupported    : true
};
