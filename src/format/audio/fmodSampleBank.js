import {Format} from "../../Format.js";

export class fmodSampleBank extends Format
{
	name           = "FMOD Sample Bank";
	website        = "http://fileformats.archiveteam.org/wiki/FMOD_Sample_Bank";
	ext            = [".fsb"];
	forbidExtMatch = true;
	magic          = ["FMOD Sample Bank format", "FMOD Sample Bank (fsb)"];
	converters     = ["vgmstream[extractAll]", "zxtune123"];
}
