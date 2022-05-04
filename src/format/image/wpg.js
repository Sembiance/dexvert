import {Format} from "../../Format.js";

export class wpg extends Format
{
	name         = "WordPerfect Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics";
	ext          = [".wpg"];
	magic        = ["WordPerfect Graphics bitmap", "WordPerfect graphic image", /^fmt\/1042( |$)/, /^x-fmt\/395( |$)/];
	mimeType     = "image/x-wpg";
	notes        = "It's a vector format, but convert doesn't always properly convert it to an SVG. So we also convert it to a PNG";
	metaProvider = ["image"];
	converters   = ["convert & convert[outType:svg]", "deark", "nconvert", `abydosconvert[format:${this.mimeType}]`, "hiJaakExpress", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"];
}
