import {Format} from "../../Format.js";

export class imperiumGalactica2GameArchive extends Format
{
	name           = "Imperium Galactica 2 Game Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_5( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:DAT_5]"];
}
