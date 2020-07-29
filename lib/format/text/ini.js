"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "INI File",
	website        : "http://fileformats.archiveteam.org/wiki/INI",
	ext            : [".ini", ".cfg", ".conf"],
	forbidExtMatch : true,
	magic          : ["Generic INItialization configuration", "Windows SYSTEM.INI", "Windows WIN.INI", "Generic INI configuration"],
	weakMagic      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
