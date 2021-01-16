"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "InstallShield Z Archive",
	website : "http://fileformats.archiveteam.org/wiki/InstallShield_Z",
	ext     : [".z"],
	magic   : ["InstallShield Z archive"]
};

exports.converterPriorty = ["isextract"];
