"use strict";
const XU = require("@sembiance/xu"),
	{BSAVE_TYPES} = require("../../program/image/deark.js");

exports.meta =
{
	name           : "QuickBasic BSAVE Image",
	website        : "http://fileformats.archiveteam.org/wiki/BSAVE_Image",
	ext            : [".art", ".pic", ".scn", ".bsv", ".cgx", ".pix", ".dat", ".pkx", ".drw"],
	forbidExtMatch : true,
	magic          : ["QuickBasic BSAVE binary data"],
	weakMagic      : true
};

// deark can't determine what type of BSAVE format it is, so we just try em all :)
exports.steps = BSAVE_TYPES.map(subType => state => ({program : "deark", flags : {dearkRemoveDups : true}, args : ["-od", state.output.dirPath, "-o", `${state.input.name}_${subType}`, "-opt", `bsave:fmt=${subType}`, state.input.filePath]}));
