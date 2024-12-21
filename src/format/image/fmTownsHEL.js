import {xu} from "xu";
import {Format} from "../../Format.js";

export class fmTownsHEL extends Format
{
	name           = "FM-Towns HEL Animation";
	website        = "http://fileformats.archiveteam.org/wiki/HEL_(FM_Towns)";
	ext            = [".hel"];
	forbidExtMatch = true;
	magic          = ["FM Towns HEL bitmap", "FM-Towns HEL Animation"];
	converters     = [
		"deark[module:fmtowns_hel][opt:fmtowns_hel:includedups] -> *ffmpeg[fps:8][outType:gif]",
		"hel2tif -> *ffmpeg[fps:8][outType:gif]"
	];
}
