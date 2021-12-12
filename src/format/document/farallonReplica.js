import {Format} from "../../Format.js";

export class farallonReplica extends Format
{
	name       = "Farallon Replica Document";
	website    = "http://fileformats.archiveteam.org/wiki/Farallon_Replica";
	ext        = [".rpl"];
	magic      = ["Farallon Replica document"];
	converters = ["replica"];
}
