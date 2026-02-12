import {Format} from "../../Format.js";

export class agonGameDataArchive extends Format
{
	name           = "Agon game data archive";
	ext            = [".sfl"];
	forbidExtMatch = true;
	magic          = ["Agon game data archive", /^geArchive: SFL_SFL10( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:SFL_SFL10]"];
}
