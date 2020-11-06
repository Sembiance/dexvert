"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://openpreservation.org/products/fido/",
	gentooPackage : "app-arch/fido",
	gentooOverlay : "dexvert",
	informational : true
};

exports.bin = () => "fido";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-q", "-noextension", "-matchprintf", "%(info.formatname)s", inPath]);
