import {Format} from "../../Format.js";

export class dng extends Format
{
	name         = "Digital Negative";
	website      = "http://fileformats.archiveteam.org/wiki/DNG";
	ext          = [".dng"];
	mimeType     = "image/x-adobe-dng";
	magic        = ["TIFF image data", /^fmt\/(436|437|438|730)( |$)/];
	weakMagic    = true;
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert", "canvas[matchType:magic]"];
}
