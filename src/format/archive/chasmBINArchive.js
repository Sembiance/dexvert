import {Format} from "../../Format.js";

export class chasmBINArchive extends Format
{
	name           = "Chasm BIN Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["Chasm BIN archive"];
	converters     = ["gameextractor"];
}
