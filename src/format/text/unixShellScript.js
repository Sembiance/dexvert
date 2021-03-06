"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Linux/UNIX/POSIX Shell Script",
	website        : "http://fileformats.archiveteam.org/wiki/Bourne_shell_script",
	ext            : [".sh", ".x11", ".gnu", ".csh", ".tsch"],
	forbidExtMatch : true,
	magic          : ["Linux/UNIX shell script", "POSIX shell script", "C shell script"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "sh"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
