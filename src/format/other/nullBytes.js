"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "All Null Bytes",
	magic     : [/^All Null Bytes$/],
	untouched : true
};

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };
