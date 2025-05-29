import {Format} from "../../Format.js";

export class fmodSampleBank extends Format
{
	name           = "FMOD Sample Bank";
	website        = "http://fileformats.archiveteam.org/wiki/FMOD_Sample_Bank";
	ext            = [".fsb", ".bank"];
	forbidExtMatch = true;
	magic          = ["FMOD Sample Bank format", "FMOD Sample Bank"];
	slow           = true;
	converters     = ["vgmstream[extractAll]", "zxtune123"];
}
