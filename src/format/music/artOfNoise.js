"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Art of Noise Module",
	website : "http://fileformats.archiveteam.org/wiki/Art_of_Noise_module",
	ext     : [".aon"],
	magic   : ["Art Of Noise Module sound file", /^Art Of Noise \d-channel module$/, "Art of Noise Tracker Song"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
