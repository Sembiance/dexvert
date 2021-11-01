"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "YMST Module",
	ext   : [".ymst"],
	magic : ["YM2149 song"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "YM-2149"}}];
