import {Format} from "../../Format.js";

export class wpg extends Format
{
	name         = "WordPerfect Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics";
	ext          = [".wpg"];
	magic        = ["WordPerfect Graphics bitmap", "WordPerfect graphic image", "Wordperfect Bild (WPG) Datei", /^fmt\/1042( |$)/, /^x-fmt\/395( |$)/];
	mimeType     = "image/x-wpg";
	notes        = "It's a vector format, but convert usually fails to produce a usable SVG";
	metaProvider = ["image"];
	converters   = ["convert", "deark[module:wpg]", "nconvert", `abydosconvert[format:${this.mimeType}]`, "keyViewPro", "photoDraw", "hiJaakExpress", "corelPhotoPaint", "pv[matchType:magic]", "canvas[matchType:magic][nonRaster]"];
}
