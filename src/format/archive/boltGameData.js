import {Format} from "../../Format.js";

export class boltGameData extends Format
{
	name       = "BOLT Game Data Archive";
	ext        = [".blt"];
	magic      = ["BOLT game data archive"];
	converters = ["gameextractor"];
}
