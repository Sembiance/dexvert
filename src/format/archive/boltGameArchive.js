import {Format} from "../../Format.js";

export class boltGameArchive extends Format
{
	name           = "BOLT Game Archive";
	ext            = [".blt"];
	forbidExtMatch = true;
	magic          = ["BOLT game data archive", /^geArchive: BLT_BOLT( |$)/];
	converters     = ["gameextractor[codes:BLT_BOLT]"];
}
