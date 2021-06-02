"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Rich Text Format",
	website        : "http://fileformats.archiveteam.org/wiki/RTF",
	ext            : [".rtf"],
	forbidExtMatch : true,
	symlinkUnsafe  : true,	// unoconv resolves symlinks and is sensitive to original extension, thus we need to forbid symlink
	magic          : ["Rich Text Format"],
	unsafe         : true
};

exports.steps = [() => ({program : "unoconv"})];
