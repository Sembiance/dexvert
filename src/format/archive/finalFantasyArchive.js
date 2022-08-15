import {Format} from "../../Format.js";

export class finalFantasyArchive extends Format
{
	name           = "Final Fantasy Game Archive";
	ext            = [".lgp"];
	forbidExtMatch = true;
	magic          = ["Final Fantasy Game Archive"];
	converters     = ["gameextractor"];
}
