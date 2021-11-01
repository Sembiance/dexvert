"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Quantum Archive",
	website : "http://fileformats.archiveteam.org/wiki/Quantum_compressed_archive",
	ext     : [".pak", ".q"],
	magic   : ["Quantum archive data", "Quantum compressed archive"]
};

exports.converterPriority = ["unpaq"];
