"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js"),
	jpg = require("./jpg.js");

exports.meta = Object.assign(XU.clone(jpg.meta), {
	name     : "JPEG - Corrupted",
	priority : C.PRIORITY.LOWEST,
	notes    : "Some JPEG files are corrupted and can't be viewed, but imageAlchemy seems to be flexible enough to handle converting them"
});
delete exports.meta.untouched;

exports.converterPriority = ["imageAlchemy"];
