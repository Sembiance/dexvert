import {Format} from "../../Format.js";

export class timexHiColor extends Format
{
	name       = "Timex 2048 Hi-Color";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 12288;
	converters = ["recoil2png"];
}
