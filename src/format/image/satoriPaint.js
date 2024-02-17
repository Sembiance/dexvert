import {Format} from "../../Format.js";

export class satoriPaint extends Format
{
	name        = "Satori Paint";
	website     = "http://fileformats.archiveteam.org/wiki/Spaceward_Graphics";
	ext         = [".cvs", ".rir"];
	magic       = ["Satori Paint Canvas", "Satori RIR scaled raster"];
	notes       = "Only sample files I've encountered shipped with the actual program, thus doesn't seem worthwhile to support this image format if the files weren't really distributed.";
	unsupported = true;
}
