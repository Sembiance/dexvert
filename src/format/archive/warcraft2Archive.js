import {Format} from "../../Format.js";

export class warcraft2Archive extends Format
{
	name       = "Warcraft 2 Archive";
	ext        = [".war"];
	magic      = ["Warcraft II game data archive"];
	converters = ["gameextractor"];
}
