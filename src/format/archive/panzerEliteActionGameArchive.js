import {Format} from "../../Format.js";

export class panzerEliteActionGameArchive extends Format
{
	name           = "Panzer Elite Action game archive";
	ext            = [".x"];
	forbidExtMatch = true;
	magic          = ["Panzer Elite Action game data archive", /^geArchive: X_XP10( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:X_XP10]"];
}
