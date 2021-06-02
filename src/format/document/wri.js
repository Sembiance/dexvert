"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Windows Write Document",
	website        : "http://fileformats.archiveteam.org/wiki/WRI",
	ext            : [".wri", ".wr", ".doc"],
	forbidExtMatch : true,
	symlinkUnsafe  : true,	// unoconv resolves symlinks and is sensitive to original extension, thus we need to forbid symlink
	magic          : ["Windows Write Document", /^Microsoft Write.* Document/, "Write for Windows Document"],
	unsafe         : true
};

exports.steps = [() => ({program : "unoconv"})];
