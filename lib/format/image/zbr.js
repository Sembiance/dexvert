"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "Zoner Zebra",
	website    : "http://fileformats.archiveteam.org/wiki/ZBR_(Zoner_Zebra)",
	ext        : [".zbr"],
	magic      : ["Zebra metafile"],
	trustMagic : true
};

exports.converterPriorty = [{program : "reaConverter", flags : { reaConverterExt : ".svg"}}, "nconvert", "deark"];
