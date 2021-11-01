"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Computer Aided Acquisition and Logistics Support",
	website  : "http://fileformats.archiveteam.org/wiki/CALS_raster",
	ext      : [".ct1", ".cal", ".ras", ".ct2", ".ct3", ".nif", ".ct4", ".c4"],
	magic    : ["CALS raster bitmap", "CALS Compressed Bitmap"]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
