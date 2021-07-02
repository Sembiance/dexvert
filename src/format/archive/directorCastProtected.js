"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Macromedia Director Cast - Protected",
	website        : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext            : [".cxt"],
	forbidExtMatch : true,
	magic          : ["Macromedia Director project", "Adobe Director Protected Cast"],
	weakMagic      : true
};

exports.converterPriorty = ["dirOpener"];
