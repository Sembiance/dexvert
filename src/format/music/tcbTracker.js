"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "TCB Tracker Module",
	ext   : [".tcb"],
	magic : ["TCB Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", "zxtune123"];
