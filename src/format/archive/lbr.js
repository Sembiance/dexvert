import {Format} from "../../Format.js";

export class lbr extends Format
{
	name       = "LBR Archive";
	website    = "http://fileformats.archiveteam.org/wiki/LBR";
	ext        = [".lbr"];
	magic      = ["LBR archive data", "LU library", /^LBR$/];
	converters = ["deark[module:lbr]", "lbrate", "unar"];
}
