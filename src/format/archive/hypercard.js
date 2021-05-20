"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "HyperCard Stack",
	website : "http://fileformats.archiveteam.org/wiki/HyperCard_stack",
	magic   : ["HyperCard Stack"]
};

// Both of these programs produce different outputs, so both are useful to use to extract data
exports.steps =
[
	() => ({program : "hypercard_dasm"}),
	() => ({program : "stackimport"})
];
