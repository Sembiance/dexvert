import {Format} from "../../Format.js";

export class darkReign2GameDataArchive extends Format
{
	name           = "Dark Reign 2 game data archive";
	ext            = [".zwp"];
	forbidExtMatch = true;
	magic          = ["Dark Reign 2 game data archive", /^geArchive: ZWP_NORK( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:ZWP_NORK]"];
}
