"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "The Final Musicsystem eXtended Module",
	ext           : [".mdat"],
	magic         : ["TFMX module sound data", "The Final Musicsystem eXtended module"],
	safeExt       : state => state.input.ext,
	keepFilename  : true,
	filesOptional : (state, otherFiles) => otherFiles
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["TFMX", "TFMX-7V", "TFMX-7V-TFHD", "TFMX-Pro", "TFMX-Pro-TFHD", "TFMX-TFHD", "TFMX_ST"].map(uadeType => ({program : "uade123", flags : {uadeType}}));
