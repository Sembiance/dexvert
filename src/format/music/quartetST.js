"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Quartet ST Module",
	ext           : [".qts"],
	safeExt       : state => state.input.ext,
	keepFilename  : true,
	filesOptional : (state, otherFiles) => otherFiles,	// Needs a corresponding smp file
	unsupported   : true,
	notes         : "So this is supported in uade123 but there is no magic to identify the files and sadly the extensions come at the start and I don't have 'prefix' match support yet. Some day."
};

//exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

//exports.converterPriority = [{program : "uade123", flags : {uadeType : "Quartet_ST"}}];
