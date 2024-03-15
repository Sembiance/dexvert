import {Format} from "../../Format.js";

export class xRes extends Format
{
	name       = "xRes Image";
	website    = "http://fileformats.archiveteam.org/wiki/XRes";
	ext        = [".lrg"];
	magic      = ["xRes multi-resolution bitmap"];
	converters = ["xRes"];
}
