"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "All Identical Bytes",
	magic     : [/^All Identical Bytes$/],
	untouched : true,
	priority  : C.PRIORITY.LOW
};

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };
