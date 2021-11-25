/*
import {Format} from "../../Format.js";

export class richardJoseph extends Format
{
	name = "Richard Joseph Module/Instrument";
	website = "http://fileformats.archiveteam.org/wiki/Richard_Joseph";
	ext = [".sng",".ins"];
	forbidExtMatch = true;
	magic = ["RJP / Vectordean module","RJP / Vectordean instrument"];
	safeExt = undefined;
	keepFilename = true;
	filesRequired = undefined;
	converters = ["uade123"]

preSteps = [null];

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Richard Joseph Module/Instrument",
	website        : "http://fileformats.archiveteam.org/wiki/Richard_Joseph",
	ext            : [".sng", ".ins"],
	forbidExtMatch : true,
	magic          : ["RJP / Vectordean module", "RJP / Vectordean instrument"],
	safeExt        : state => state.input.ext,
	keepFilename   : true,
	// Both .sng and .ins are required
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===(state.input.name.toLowerCase() + exports.meta.ext.find(ext => ext!==state.input.ext.toLowerCase())))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".ins"; }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];

*/
