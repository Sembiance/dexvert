"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Farbfeld",
	website  : "http://fileformats.archiveteam.org/wiki/Farbfeld",
	ext      : [".ff"],
	mimeType : "image/x-farbfeld",
	magic    : [/[Ff]arbfeld ([Ii]mage|bitmap)/]
};

exports.converterPriority = ["deark", "abydosconvert"];
