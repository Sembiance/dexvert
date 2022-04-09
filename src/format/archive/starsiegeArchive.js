import {Format} from "../../Format.js";

export class starsiegeArchive extends Format
{
	name           = "Starsiege Archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = ["Starsiege game data archive", "Starsiege Tribes game data archive"];
	converters     = ["gameextractor"];
}
