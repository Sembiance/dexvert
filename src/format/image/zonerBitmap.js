import {Format} from "../../Format.js";

export class zonerBitmap extends Format
{
	name       = "Zoner Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/BMI_(Zoner)";
	ext        = [".bmi"];
	magic      = ["Zoner BMI Bitmap", "deark: bmi"];
	converters = ["deark[module:bmi]"];
}
