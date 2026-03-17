import {Format} from "../../Format.js";

export class runesOfMagicGameArchive extends Format
{
	name           = "Runes of Magic Game Archive";
	ext            = [".fdb"];
	forbidExtMatch = true;
	magic          = ["Runes of Magic game data archive", /^geArchive: FDB_BDF( |$)/];
	converters     = ["gameextractor[codes:FDB_BDF]"];
}
