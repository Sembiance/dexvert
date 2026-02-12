import {Format} from "../../Format.js";

export class empireEarth1GameArchive extends Format
{
	name           = "Empire Earth 1 Game Archive";
	ext            = [".ssa"];
	forbidExtMatch = true;
	magic          = ["Empire Earth 1 game data", "Empire Earth Game Archive", /^geArchive: SSA_RASS( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:SSA_RASS]"];
}
