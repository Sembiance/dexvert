"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "C.js"));

exports.meta =
{
	website       : "http://dag.wiee.rs/home-made/unoconv/",
	gentooPackage : "app-office/unoconv"
};

exports.bin = () => "unoconv";
exports.args = state =>
{
	if(state.id.family==="image")
		state.unoconvType = "png";
	else if(state.id.family==="vector")
		state.unoconvType = "svg";
	else
		state.unoconvType = "pdf";

	return ["-n", "-p", `${C.UNOCONV_PORT}`, "-f", state.unoconvType, "-o", path.join(state.output.dirPath, `outfile.${state.unoconvType}`), state.input.filePath];
};

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, `outfile.${state.unoconvType}`), path.join(state.output.absolute, `${state.input.name}.${state.unoconvType}`))(state, p, cb);
