"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Actionamics Sound Tool Module",
	ext   : [".ast"],
	magic : ["Actionamics Sound Tool module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
