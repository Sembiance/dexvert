import {Format} from "../../Format.js";

export class eot extends Format
{
	name       = "Embedded OpenType";
	website    = "http://fileformats.archiveteam.org/wiki/Embedded_OpenType";
	ext        = [".eot", ".fntdata"];
	magic      = ["Embedded OpenType"];
	converters = ["eot2ttf"];
}
