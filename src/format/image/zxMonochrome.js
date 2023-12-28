import {Format} from "../../Format.js";

export class zxMonochrome extends Format
{
	name       = "ZX Monochrome";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 6144;
	converters = ["recoil2png"];
}
