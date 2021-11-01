"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Lionheart Module",
	ext   : [".lion"],
	magic : ["Lionheart module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
