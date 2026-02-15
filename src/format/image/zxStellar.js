import {Format} from "../../Format.js";

export class zxStellar extends Format
{
	name       = "ZX Spectrum Stellar";
	website    = "http://fileformats.archiveteam.org/wiki/STL_(ZX_Spectrum)";
	ext        = [".stl"];
	fileSize   = 3072;
	converters = ["recoil2png[format:STL]"];
}
