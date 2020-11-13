"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AMOS Basic Source Code Archive",
	website : "http://fileformats.archiveteam.org/wiki/AMOS_BASIC_tokenized_file",
	ext     : [".amos"],
	magic   : ["AMOS Basic source code", "AMOS Pro source"]
};

exports.steps = [() => ({program : "listamos"}), () => ({program : "dumpamos"})];
