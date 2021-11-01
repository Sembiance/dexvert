"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "FS-UAE Meta File",
	website       : "https://fs-uae.net/docs/options/uaem-write-flags",
	ext           : [".uaem"],
	magic         : [...C.TEXT_MAGIC, "FS-UAE file metadata"],
	weakMagic     : true,
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}`),
	untouched     : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
