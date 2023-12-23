import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class farallonReplica extends Format
{
	name           = "Farallon Replica Document";
	website        = "http://fileformats.archiveteam.org/wiki/Farallon_Replica";
	ext            = [".rpl"];
	magic          = ["Farallon Replica document"];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["replica"];
}
