import {Format} from "../../Format.js";

export class hru extends Format
{
	name       = "HRU";
	website    = "http://fileformats.archiveteam.org/wiki/HRU";
	ext        = [".hru"];
	converters = ["nconvert"];
}
