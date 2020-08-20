"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "SGX Graphics File Format",
	website        : "http://fileformats.archiveteam.org/wiki/SGX",
	ext            : [".sgx", ".svg"],
	forbidExtMatch : true,
	magic          : ["SuperView Graphics bitmap"],
	unsupported    : true,
	notes          : "No known converter."
};
