"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "InfoFile Database File",
	ext            : [".flr"],
	forbidExtMatch : true,
	magic          : ["InfoFile database"],
	weakMagic      : true,
	notes          : "Very obscure amiga database program."
};

exports.converterPriority = ["strings"];
