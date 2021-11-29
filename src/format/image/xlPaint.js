import {Format} from "../../Format.js";

export class xlPaint extends Format
{
	name       = "XL-Paint";
	website    = "http://fileformats.archiveteam.org/wiki/XL-Paint";
	ext        = [".xlp", ".max", ".raw"];
	magic      = ["XL-Paint MAX bitmap"];
	fileSize   = {".raw" : [792, 15372]};
	converters = ["recoil2png"];
}
