"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Silmarils Module",
	ext  : [".mok"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "Silmarils"}}];
