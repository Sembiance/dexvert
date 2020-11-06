"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require("../../C.js");

exports.meta =
{
	website       : "http://dag.wiee.rs/home-made/unoconv/",
	gentooPackage : "app-office/unoconv",
	bruteUnsafe   : true
};

exports.bin = () => "unoconv";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile.${(state.unoconvType || (state.id.family==="image" ? "png" : "pdf"))}`)) => [
	"-n", "-p", `${C.UNOCONV_PORT}`, "-f", (state.unoconvType || (state.id.family==="image" ? "png" : "pdf")), "-o", outPath, inPath];

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile.${(state.unoconvType || (state.id.family==="image" ? "png" : "pdf"))}`),
	path.join(state.output.absolute, `${state.input.name}.${(state.unoconvType || (state.id.family==="image" ? "png" : "pdf"))}`))(state, p, cb);
