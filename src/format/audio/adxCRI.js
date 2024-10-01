import {xu} from "xu";
import {Format} from "../../Format.js";

export class adxCRI extends Format
{
	name       = "CRI ADX";
	ext        = [".adx"];
	magic      = ["ADX lossy compressed audio", "CRI ADX ADPCM audio", "CRI ADX (adx)", /^fmt\/840( |$)/];
	converters = ["ffmpeg[format:adx][outType:mp3]", "vgmstream"];
}
