"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "GlueMon Module",
	ext   : [".glue"],
	magic : ["GlueMon module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
