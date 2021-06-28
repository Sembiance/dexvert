"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MovieSetter Video",
	website : "http://fileformats.archiveteam.org/wiki/MovieSetter",
	magic   : ["MovieSetter movie"],
	notes   : "Xanim doesn't play sound and couldn't find another linux based converter that supports sound. Only known solution now would be to convert it on a virtual amiga with MovieSetter itself probably."
};

exports.converterPriorty = ["xanim"];
