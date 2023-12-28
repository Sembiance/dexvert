import {Format} from "../../Format.js";

export class timexHiResGigascreen extends Format
{
	name       = "Timex 2048 Hi-Res Gigascreen";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".hrg"];
	fileSize   = 24578;
	converters = ["recoil2png"];
}
