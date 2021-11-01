"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Imagic",
	website : "http://fileformats.archiveteam.org/wiki/Imagic_Film/Picture",
	ext     : [".ic1", ".ic2", ".ic3"],
	magic   : ["Imagic picture/animation bitmap"]
};

exports.converterPriority = ["recoil2png"];
