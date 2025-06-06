import {Format} from "../../Format.js";

export class sunRaster extends Format
{
	name           = "Sun Raster Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Sun_Raster";
	ext            = [".ras", ".rast", ".rs", ".scr", ".sr", ".sun", ".im1", ".im8", ".im24", ".im32"];
	forbidExtMatch = [".scr"];
	mimeType       = "image/x-sun-raster";
	magic          = ["Sun Raster bitmap", "image/x-sun-raster", /^Sun [Rr]aster [Ii]mage/, "piped sunrast sequence (sunrast_pipe)", "deark: sunras", "Sun Raster File :ras:", /^x-fmt\/184( |$)/];
	idMeta         = ({macFileType}) => macFileType==="SUNn";

	// abydosconvert also supports this format, but it hangs in an infinite loop when passing it an invalid image, so we don't bother including it below
	converters = [
		"deark[module:sunras]", "gimp", "nconvert[format:ras]", "wuimg", "imconv[format:ras][matchType:magic]",
		"canvas[matchType:magic]", "picturePublisher[matchType:magic]", "pv[matchType:magic]", "keyViewPro[matchType:magic]"
	];
}
