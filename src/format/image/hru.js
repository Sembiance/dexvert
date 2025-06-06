import {Format} from "../../Format.js";

export class hru extends Format
{
	name       = "HRU";
	website    = "http://fileformats.archiveteam.org/wiki/HRU";
	magic      = ["HRU bitmap", "HRU :hru:"];
	ext        = [".hru"];
	converters = ["nconvert[format:hru]"];
}
