import {Format} from "../../Format.js";

export class xface extends Format
{
	name       = "X-face Image";
	website    = "http://fileformats.archiveteam.org/wiki/X-Face";
	magic      = ["deark: xface"];
	converters = ["deark[module:xface]"];
}
