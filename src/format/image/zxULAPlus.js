import {Format} from "../../Format.js";

export class zxULAPlus extends Format
{
	name       = "ZX Spectrum ULA+";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 6976;
	converters = ["recoil2png"];
}
