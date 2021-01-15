"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Empty File",
	magic     : [/^empty$/],
	untouched : true
};

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };
