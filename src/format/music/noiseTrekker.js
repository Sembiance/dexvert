"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "NoiseTrekker Module",
	website     : "http://fileformats.archiveteam.org/wiki/Noisetrekker_module",
	ext         : [".ntk"],
	magic       : [/^NoiseTrekker v\d\.\d module$/],
	unsupported : true
};
