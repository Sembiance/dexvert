"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.openssl.org/",
	gentooPackage  : "dev-libs/openssl",
	gentooUseFlags : "asm zlib",
	flags :
	{
		sslCommand   : "Which command to perform. REQUIRED FLAG",
		encodingType : "Encoding type of the certificate. Default: Let openssl decide (usually fails)"
	},
	unsafe : true
};

exports.bin = () => "openssl";
exports.args = (state, p, r, inPath=state.input.filePath) =>
{
	const args = [r.flags.sslCommand, "-noout", "-text"];
	if(r.flags.encodingType)
		args.push("-inform", r.flags.encodingType);
		
	return [...args, "-in", inPath];
};
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.txt`);
