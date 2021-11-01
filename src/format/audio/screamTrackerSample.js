"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Scream Tracker Sample",
	ext            : [".snd", ".s3i", ".smp"],
	forbidExtMatch : true,
	magic          : ["Scream Tracker Sample", "Scream Tracker/Digiplayer sample"]
};

exports.converterPriority = ["awaveStudio"];
