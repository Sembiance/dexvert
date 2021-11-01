"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Wildcat! WCX",
	ext            : [".wcx"],
	forbidExtMatch : true,
	magic          : ["Wildcat WCX"],
	weakMagic      : true
};

exports.converterPriority = ["wccnosy"];
