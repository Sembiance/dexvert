import {Format} from "../../Format.js";

export class mechWarrior4GameData extends Format
{
	name           = "MechWarrior 4 game data";
	ext            = [".mw4"];
	forbidExtMatch = true;
	magic          = ["MechWarrior 4 game data", /^geArchive: MW4_VBD( |$)/];
	converters     = ["gameextractor[codes:MW4_VBD]"];
}
