import {Format} from "../../Format.js";

export class etherlords2GameDataArchive extends Format
{
	name           = "Etherlords 2 game data archive";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["Etherlords 2 game data archive", /^geArchive: (RES|RES_8)( |$)/];
	converters     = ["gameextractor[codes:RES_8,RES]"];
}
