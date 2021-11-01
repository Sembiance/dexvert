"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "GNU Info File",
	ext            : [".info-1", ".info-2", ".info-3", ".info-4", ".info-5", ".info-6", ".info-7", ".info-8", ".info-9"],
	forbidExtMatch : true,
	magic          : [/^GNU Info$/]		// We do NOT include Trid's "GNU Info document" because it's a bit too loose
};

exports.converterPriority = ["strings"];
