import {Format} from "../../Format.js";

export class dungeonSiege2Resource extends Format
{
	name           = "Dungeon Siege 2 Resource";
	ext            = [".ds2res"];
	forbidExtMatch = true;
	magic          = ["Dungeon Siege 2 data", /^geArchive: DS2RES_DSG2TANK( |$)/];
	converters     = ["gameextractor[codes:DS2RES_DSG2TANK]"];
}
