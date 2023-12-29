import {Format} from "../../Format.js";

export class timexHiRes extends Format
{
	name       = "Timex 2048 Hi-Res";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 12289;
	converters = ["recoil2png"];
}
