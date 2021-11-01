"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Empty File",
	magic     : [/^empty$/],
	untouched : true
};

// Don't allow transformed files to be counted for this 'catch all' type format
exports.idCheck = state => !state.transformed;

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };
