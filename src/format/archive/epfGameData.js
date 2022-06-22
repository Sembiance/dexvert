import {Format} from "../../Format.js";

export class epfGameData extends Format
{
	name       = "EPF Game Data Archive";
	ext        = [".epf"];
	magic      = ["EPF game data archive"];
	converters = ["gameextractor"];
}
