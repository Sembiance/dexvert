"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Common Ground",
	website        : "http://fileformats.archiveteam.org/wiki/Common_Ground",
	ext            : [".dp"],
	forbidExtMatch : true,
	magic          : ["Common Ground Digital Paper document"],
	notes          : "Can probably only be converted properly with the Common Ground software itself, which I was unable to locate."
};

exports.converterPriority = ["strings"];
