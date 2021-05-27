"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name        : "FM-TownsOS App",
	ext         : [".exp"],
	magic       : ["FM-TownsOS EXP"],
	weakMagic   : true,
	unsupported : true
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x50, 0x33])) || file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x4D, 0x50]));
