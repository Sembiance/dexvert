import {Format} from "../../Format.js";

export class descentArchive extends Format
{
	name       = "Descent Archive";
	ext        = [".hog"];
	magic      = ["Descent game data archive"];
	converters = ["gamearch", "gameextractor"];
}
