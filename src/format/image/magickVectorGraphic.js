import {Format} from "../../Format.js";

export class magickVectorGraphic extends Format
{
	name         = "Magick Vector Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/Acorn_Draw";
	ext          = [".mvg"];
	magic        = ["Magick Vector Graphics", /^ImageMagick Vector Graphic/];
	metaProvider = ["image"];
	converters   = [
		// verctor
		"convert[format:mvg][outType:svg] -> inkscape",		// the SVG file that imagemagick produces is missing the 'xmlns' attribute, so we re-convert it to SVG with inkscape

		// raster
		"konvertor[matchType:magic]"
	];
}
