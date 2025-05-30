import {Format} from "../../Format.js";

export class naiveNIA extends Format
{
	name       = "Naïve Image Format NIA";
	website    = "http://fileformats.archiveteam.org/wiki/Naïve_Image_Formats";
	ext        = [".nia"];
	mimeType   = "image/nia";
	magic      = ["Naive Image format NIA animated bitmaps", "deark: nie (NIA)"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
