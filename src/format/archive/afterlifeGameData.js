import {Format} from "../../Format.js";

export class afterlifeGameData extends Format
{
	name           = "Afterlife game data";
	ext            = [".000"];
	forbidExtMatch = true;
	magic          = ["Afterlife game data", /^geArchive: 000_FFIJ( |$)/];
	converters     = ["gameextractor[codes:000_FFIJ]"];
}
