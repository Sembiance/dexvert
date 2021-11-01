"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Module Description File",
	website        : "https://www.cubic.org/player/doc/node73.htm",
	ext            : [".mdz"],
	forbidExtMatch : true,
	magic          : ["Open Cubic Player Module Information MDZ"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
