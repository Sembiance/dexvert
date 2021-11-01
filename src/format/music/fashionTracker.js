"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Fashion Tracker Module",
	ext   : [".ex"],
	magic : ["Fashion Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
