"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Portfolio PGX",
	website : "http://fileformats.archiveteam.org/wiki/PGX_(Portfolio)",
	ext     : [".pgx"],
	magic   : ["Portfolio PGX bitmap"],
	notes   : "Sometimes instead of a single bitmap, it's multiple frames to a animation which we then convert into an MP4."
};

exports.converterPriority = [{program : "deark", flags : {dearkKeepAsGIF : true, dearkJoinFrames : true}}];
