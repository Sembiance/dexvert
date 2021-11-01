"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/Sembiance/inivalidate",
	gentooPackage : "app-arch/inivalidate",
	gentooOverlay : "dexvert",
	informational : true
};

exports.bin = () => "inivalidate";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	r.meta = JSON.parse((r.results || "").trim());
	setImmediate(cb);
};
