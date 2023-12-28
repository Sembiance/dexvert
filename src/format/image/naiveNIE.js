import {Format} from "../../Format.js";

export class naiveNIE extends Format
{
	name       = "Naïve Image Format NIE";
	website    = "http://fileformats.archiveteam.org/wiki/Naïve_Image_Formats";
	ext        = [".nie"];
	mimeType   = "image/nie";
	magic      = ["Naive Image format NIE bitmap"];
	converters = ["deark[module:nie]", `abydosconvert[format:${this.mimeType}]`];
}
