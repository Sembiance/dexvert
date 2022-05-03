import {Format} from "../../Format.js";

export class sunRaster extends Format
{
	name     = "Sun Raster Bitmap";
	website  = "http://fileformats.archiveteam.org/wiki/Sun_Raster";
	ext      = [".ras", ".rast", ".rs", ".scr", ".sr", ".sun", ".im1", ".im8", ".im24", ".im32"];
	weakExt  = [".scr"];
	mimeType = "image/x-sun-raster";
	magic    = ["Sun Raster bitmap", /^Sun [Rr]aster [Ii]mage/];

	// abydosconvert also supports this format, but it hangs in an infinite loop when passing it an invalid image, so we don't bother including it below
	converters = ["deark", "gimp", "nconvert", "canvas"];
}
