import {Format} from "../../Format.js";

export class madsHAG extends Format
{
	name       = "MADS HAG";
	ext        = [".hag"];
	magic      = ["MADS HAG game data archive"];
	converters = ["gameextractor"];
}
