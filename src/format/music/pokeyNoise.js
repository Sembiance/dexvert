/*
import {Format} from "../../Format.js";

export class pokeyNoise extends Format
{
	name = "PokeyNoise Module";
	ext = [".pn"];
	magic = ["PokeyNoise chiptune"];
	safeExt = undefined;
	keepFilename = true;
	filesOptional = undefined;
	converters = [{"program":"uade123","flags":{"uadeType":"Pokeynoise"}}]

metaProviders = [""];
}
*/
/*
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

*/
