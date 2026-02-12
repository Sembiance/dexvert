import {Format} from "../../Format.js";

export class warriorKingsGameData extends Format
{
	name           = "Warrior Kings game data";
	ext            = [".bcp"];
	forbidExtMatch = true;
	magic          = ["Warrior Kings game data", /^geArchive: BCP_PAKFILE2( |$)/];
	converters     = ["gameextractor[codes:BCP_PAKFILE2]"];
}
