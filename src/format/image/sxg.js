import {Format} from "../../Format.js";

export class sxg extends Format
{
	name       = "Speccy eXtended Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/SXG_(ZX_Spectrum)";
	ext        = [".sxg"];
	magic      = ["Speccy eXtended Graphics bitmap"];
	converters = ["recoil2png"];
}
