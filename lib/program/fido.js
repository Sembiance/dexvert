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
exports.args = state => (["-q", "-noextension", "-matchprintf", "%(info.formatname)s", state.input.filePath]);
