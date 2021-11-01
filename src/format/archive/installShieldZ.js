"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "InstallShield Z Archive",
	website : "http://fileformats.archiveteam.org/wiki/InstallShield_Z",
	ext     : [".z"],
	magic   : ["InstallShield Z archive"]
};

exports.converterPriority = ["isextract", {program : "UniExtract", flags : {uniExtractType : "i3comp extraction"}}, {program : "UniExtract", flags : {uniExtractType : "STIX extraction"}}];
