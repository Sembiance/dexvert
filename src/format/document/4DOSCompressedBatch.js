"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "4DOS Compressed Batch-To-Memory File",
	ext   : [".btm"],
	magic : ["4DOS compressed Batch-To-Memory"]
};

exports.converterPriority = ["4decomp"];
