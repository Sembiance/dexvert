import {Format} from "../../Format.js";

export class heic extends Format
{
	name         = "High Efficiency Image File";
	website      = "http://fileformats.archiveteam.org/wiki/HEIF";
	ext          = [".heic", ".heif"];
	mimeType     = "image/heic";
	magic        = ["HEIF bitmap", "High Efficiency Image File Format", "ISO Media, HEIF Image", /^fmt\/1101( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "iconvert", "gimp"];
}
