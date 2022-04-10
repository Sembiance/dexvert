import {Format} from "../../Format.js";

export class fuzzyBitmap extends Format
{
	name       = "Fuzzy Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/FBM_image";
	ext        = [".fbm", ".cbm"];
	magic      = ["Fuzzy Bitmap", "FBM image data"];
	converters = ["fbm2tga", "nconvert"];
}
