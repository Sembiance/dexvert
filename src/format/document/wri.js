"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Windows Write Document",
	website        : "http://fileformats.archiveteam.org/wiki/WRI",
	ext            : [".wri", ".wr", ".doc"],
	forbidExtMatch : true,
	magic          : ["Windows Write Document", /^Microsoft Write.* Document/, "Write for Windows Document"],
	unsafe         : true
};

exports.steps = [() => ({program : "unoconv"})];
