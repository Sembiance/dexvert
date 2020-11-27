"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "WordPerfect document",
	website     : "http://fileformats.archiveteam.org/wiki/WordPerfect",
	ext         : [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"],
	magic       : [/^WordPerfect.* [Dd]ocument/],
	weakMagic   : true,
	bruteUnsafe : true
};

exports.steps = [() => ({program : "unoconv"})];
