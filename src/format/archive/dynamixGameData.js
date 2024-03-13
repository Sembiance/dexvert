import {Format} from "../../Format.js";

export class dynamixGameData extends Format
{
	name       = "Dynamix Game Data Archive";
	ext        = [".dyn"];
	magic      = ["Dynamix game data archive", "Dynamix Volume File game data archive"];
	converters = ["gameextractor"];
}
