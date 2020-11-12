"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://openpreservation.org/products/fido/",
	gentooPackage : "app-arch/fido",
	gentooOverlay : "dexvert",
	informational : true,
	notes         : "This is no longer actually used by dexvert. First it's pretty slow, about 400ms just to load and id something. Second, 99% of what it detects can be detected with trid/file. Lastly it's a bit loose and identifies files incorrectly."
};

exports.bin = () => "fido";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-q", "-noextension", "-matchprintf", "%(info.formatname)s", inPath]);
