/*
import {Format} from "../../Format.js";

export class identicalBytes extends Format
{
	name = "All Identical Bytes";
	magic = [{}];
	untouched = true;
	priority = 3;

idCheck = undefined;

updateProcessed = undefined;
}
*/
/*
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

// Don't allow transformed files to be counted for this 'catch all' type format
exports.idCheck = state => !state.transformed;

exports.updateProcessed = (state, p, cb) => { state.processed = true; setImmediate(cb); };

*/
