"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Covox ADPCM Encoded Audio",
	website : "https://wiki.multimedia.cx/index.php/Covox_ADPCM",
	ext     : [".v8", ".cvx"],
	magic   : ["Covox ADPCM encoded audio"]
};

exports.steps = [() => ({program : "awaveStudio"})];
