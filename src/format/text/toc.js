"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "CDRDAO TOC File",
	website : "http://cdrdao.sourceforge.net/example.html#toc-file-example",
	ext     : [".toc"]
};

exports.steps = [() => ({program : "toc2cue"})];
