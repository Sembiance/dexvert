"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Windows Write Document",
	website     : "http://fileformats.archiveteam.org/wiki/WRI",
	ext         : [".wri"],
	magic       : ["Windows Write Document", /^Microsoft Write.* Document/, "Write for Windows Document"],
	bruteUnsafe : true
};

exports.steps = [() => ({program : "unoconv"})];
