"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://mark0.net/soft-trid-e.html",
	gentooPackage : "app-arch/trid",
	gentooOverlay : "dexvert",
	informational : true
};

exports.bin = () => "trid";
exports.args = state => ([state.input.filePath, "-n:5"]);
