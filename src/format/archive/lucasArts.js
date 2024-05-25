import {Format} from "../../Format.js";

export class lucasArts extends Format
{
	name       = "Lucas Arts Game Data Archive";
	ext        = [".gob"];
	magic      = ["LucasArts Game data archive", "Dark Forces Game data archive"];
	converters = ["gameextractor"];
}
