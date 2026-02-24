import {Format} from "../../Format.js";

export class starWarsBattlefrontGameDataArchive extends Format
{
	name           = "Star Wars Battlefront game data archive";
	ext            = [".lvl"];
	forbidExtMatch = true;
	magic          = ["Star Wars Battlefront game data archive", /^geArchive: (LVL_UCFB_2|LVL_UCFB)( |$)/];
	converters     = ["gameextractor[codes:LVL_UCFB_2,LVL_UCFB]"];
}
