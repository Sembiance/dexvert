"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "WordPerfect Graphic",
	website  : "http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics",
	ext      : [".wpg"],
	magic    : ["WordPerfect Graphics bitmap", "WordPerfect graphic image"]
};

exports.preSteps = [state => { state.convertExt = ".svg"; }];
exports.converterPriorty = ["convert"];
exports.postSteps = [state => { delete state.convertExt; }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
