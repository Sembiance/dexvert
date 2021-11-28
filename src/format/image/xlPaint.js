import {Format} from "../../Format.js";

export class xlPaint extends Format
{
	name       = "XL-Paint";
	website    = "http://fileformats.archiveteam.org/wiki/XL-Paint";
	ext        = [".xlp", ".max", ".raw"];
	magic      = ["XL-Paint MAX bitmap"];
	fileSize   = {".raw" : [792, 15372]};
	priority   = this.PRIORITY.HIGH;	// When it comes to 'ext' matching .raw and .max, it's more likely this then it is the other .raw extension formats (really rob?)
	converters = ["recoil2png"];
}
