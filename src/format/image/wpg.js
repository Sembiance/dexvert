import {Format} from "../../Format.js";

export class wpg extends Format
{
	name         = "WordPerfect Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics";
	ext          = [".wpg"];
	magic        = ["WordPerfect Graphics bitmap", "WordPerfect graphic image", "WordPerfect graphics", "Wordperfect Bild (WPG) Datei", "deark: wpg", "Word Perfect Bitmap :wpg:", /^fmt\/1042( |$)/, /^x-fmt\/395( |$)/];
	idMeta       = ({macFileType}) => macFileType==="WPGf";
	mimeType     = "image/x-wpg";
	notes        = "It's a vector format, but convert usually fails to produce a usable SVG and often was used just to store a raster image, so we don't even bother trying to convert to SVG";
	metaProvider = ["image"];
	converters   = [
		"convert", "deark[module:wpg]", "nconvert[format:wpg]", `abydosconvert[format:${this.mimeType}]`,
		"keyViewPro", "photoDraw", "hiJaakExpress", "corelPhotoPaint", "pv[matchType:magic]", "canvas5[matchType:magic][vector]", "canvas[matchType:magic][nonRaster]"];
}
