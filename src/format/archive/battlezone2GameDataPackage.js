import {Format} from "../../Format.js";

export class battlezone2GameDataPackage extends Format
{
	name           = "Battlezone 2 game data package";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["Battlezone 2 game data package", /^geArchive: PAK_DOCP( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:PAK_DOCP]"];
}
