import {Format} from "../../Format.js";

export class zxAtr extends Format
{
	name       = "ZX Spectrum Attributes Image";
	website    = "http://fileformats.archiveteam.org/wiki/ATR_(ZX_Spectrum)";
	ext        = [".atr"];
	fileSize   = 768;
	converters = ["recoil2png"];
}
