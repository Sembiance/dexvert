"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SimTex LBX Game Data",
	ext     : [".lbx"],
	magic   : ["SimTex LBX game data container"]
};

exports.converterPriority = ["gameextractor"];
