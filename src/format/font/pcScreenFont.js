import {Format} from "../../Format.js";

export class pcScreenFont extends Format
{
	name       = "PC Screen Font";
	website    = "http://fileformats.archiveteam.org/wiki/PC_Screen_Font";
	ext        = [".psf", ".psfu"];
	magic      = [/PC Screen Font/];
	converters = ["deark[module:psf]"];
}
