"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Word Document",
	website        : "http://fileformats.archiveteam.org/wiki/DOC",
	ext            : [".doc"],
	forbidExtMatch : true,
	symlinkUnsafe  : true,	// unoconv resolves symlinks and is sensitive to original extension, thus we need to forbid symlink
	magic          : ["Microsoft Word document"],
	unsafe         : true
};

exports.steps = [() => ({program : "unoconv"})];
