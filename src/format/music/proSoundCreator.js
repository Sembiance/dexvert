import {Format} from "../../Format.js";

export class proSoundCreator extends Format
{
	name         = "Pro Sound Creator";
	ext          = [".psc"];
	magic        = ["Spectrum Pro Sound Creator chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[matchType:magic]"];
}
