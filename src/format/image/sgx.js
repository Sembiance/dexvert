"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "SGX Graphics File Format",
	website        : "http://fileformats.archiveteam.org/wiki/SGX",
	ext            : [".sgx", ".svg"],
	forbidExtMatch : true,
	magic          : ["SuperView Graphics bitmap", "SGX Graphics bitmap"],
	mimeType       : "image/x-superview",
	notes          : "Some image files are not yet supported such as testimg-lz77.sgx"
};

exports.converterPriorty = ["abydosconvert"];
