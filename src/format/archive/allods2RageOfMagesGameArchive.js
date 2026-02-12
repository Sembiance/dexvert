import {Format} from "../../Format.js";

export class allods2RageOfMagesGameArchive extends Format
{
	name           = "Allods 2 Rage Of Mages game archive";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["Allods 2 Rage Of Mages game data archive", /^geArchive: RES_2( |$)/];
	converters     = ["gameextractor[codes:RES_2]"];
}
