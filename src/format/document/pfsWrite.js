"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Professional Write Document",
	magic : ["Professional Write document"]
};

exports.converterPriority = [{program : "fileMerlin", flags : {fileMerlinSrcFormat : "PFS*"}}];
