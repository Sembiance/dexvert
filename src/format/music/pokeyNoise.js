"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "PokeyNoise Module",
	ext           : [".pn"],
	magic         : ["PokeyNoise chiptune"],
	safeExt       : state => state.input.ext,
	keepFilename  : true,
	filesOptional : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.base.toLowerCase()}.info`)
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "Pokeynoise"}}];
