import {Format} from "../../Format.js";

export class pcrFont extends Format
{
	name           = "PCR Font";
	website        = "http://fileformats.archiveteam.org/wiki/PCR_font";
	ext            = [".pcr"];
	fileSize       = 3595;
	forbidExtMatch = true;
	magic          = ["PCR Font"];
	converters     = ["deark[module:pcrfont]"];
}
