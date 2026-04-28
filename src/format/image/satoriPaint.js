import {Format} from "../../Format.js";

export class satoriPaint extends Format
{
	name        = "Satori Paint";
	website     = "http://fileformats.archiveteam.org/wiki/Spaceward_Graphics";
	ext         = [".cvs", ".rir"];
	magic       = ["Satori Paint Canvas", "Satori RIR scaled raster"];
	unsupported = true;	// while there are 229 unique files on discmaster, they all apear to be ones distributed with the program itself, so not very exciting to support
}
