import {Format} from "../../Format.js";

export class sxg extends Format
{
	name       = "Speccy eXtended Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/SXG_(ZX_Spectrum)";
	ext        = [".sxg"];
	magic      = ["Speccy eXtended Graphics bitmap", /^fmt\/1583( |$)/];
	converters = ["recoil2png[format:SXG]"];
}
