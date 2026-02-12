import {Format} from "../../Format.js";

export class gameMakerStudioGameDataArchive extends Format
{
	name           = "GameMaker Studio game data archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["GameMaker Studio game data archive", /^geArchive: DAT_FORM( |$)/];
	weakMagic      = ["GameMaker Studio game data archive"];
	converters     = ["gameextractor[codes:DAT_FORM]"];
}
