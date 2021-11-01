"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Microfox PUT Archive",
	website        : "http://fileformats.archiveteam.org/wiki/PUT",
	ext            : [".put", ".ins"],
	forbidExtMatch : true,
	magic          : ["Microfox Company PUT compressed archive", "PUT archive data"]
};

exports.converterPriority = ["microfoxGET"];
