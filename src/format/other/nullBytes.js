"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "All Null Bytes",
	/// WARNING: Do not match 'null bytes' from trid, it only checks the first X bytes for zeroes. So NOT trustworthy
	magic     : [/^All Null Bytes$/],
	untouched : true
};

// Don't allow transformed files to be counted for this 'catch all' type format
exports.idCheck = state => !state.transformed;

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };
