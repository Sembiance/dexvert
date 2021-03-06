"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Scream Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/S3M",
	ext     : [".s3m", ".stm"],
	magic   : ["ScreamTracker III Module sound data", "Scream Tracker 3 module", "Scream Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp", "zxtune123"];
