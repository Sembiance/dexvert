"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "WordPerfect document",
	website     : "http://fileformats.archiveteam.org/wiki/WordPerfect",
	ext         : [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7"],
	magic       : [/^WordPerfect.* [Dd]ocument/],
	bruteUnsafe : true
};

exports.steps = [() => ({program : "unoconv"})];
