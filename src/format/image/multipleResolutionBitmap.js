import {Format} from "../../Format.js";

export class multipleResolutionBitmap extends Format
{
	name       = "Multiple Resolution Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Segmented_Hypergraphics";
	ext        = [".mrb"];
	magic      = ["Multiple Resolution Bitmap", "deark: shg (SHG)"];
	converters = ["deark[module:shg]"];
}
