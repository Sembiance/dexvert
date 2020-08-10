"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "Calamus Vector Graphic",
	website : "http://fileformats.archiveteam.org/wiki/Calamus_Vector_Graphic",
	ext     : [".cvg"],
	magic   : ["Calamus Vector Graphic"]
};

exports.steps =
[
	() => ({program : "scribus"}),
	(state, p) => p.family.validateOutputFiles
];
