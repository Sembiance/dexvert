/*
import {Format} from "../../Format.js";

export class iffANIM extends Format
{
	name = "Interchange File Format Animation";
	website = "http://fileformats.archiveteam.org/wiki/ANIM";
	ext = [".anim",".anm",".sndanim"];
	magic = ["IFF data, ANIM animation","IFF ANIM"];
	converters = [{"program":"ffmpeg","flags":{"ffmpegFormat":"iff"}},{"program":"xanim","flags":{"xanimDelay":6}}]

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Interchange File Format Animation",
	website  : "http://fileformats.archiveteam.org/wiki/ANIM",
	ext      : [".anim", ".anm", ".sndanim"],
	magic    : ["IFF data, ANIM animation", "IFF ANIM"]
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "iff"}}, {program : "xanim", flags : {xanimDelay : 6}}];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
