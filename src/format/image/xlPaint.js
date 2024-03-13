import {Format} from "../../Format.js";

export class xlPaint extends Format
{
	name       = "XL-Paint";
	website    = "http://fileformats.archiveteam.org/wiki/XL-Paint";
	ext        = [".xlp", ".max", ".raw"];
	magic      = ["XL-Paint MAX bitmap", /^fmt\/(1658|1659)( |$)/];
	fileSize   = {".raw" : [792, 15372]};
	converters = ["recoil2png"];
}
