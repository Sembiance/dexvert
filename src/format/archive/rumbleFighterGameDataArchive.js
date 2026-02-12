import {Format} from "../../Format.js";

export class rumbleFighterGameDataArchive extends Format
{
	name           = "Rumble Fighter game data archive";
	ext            = [".nsz"];
	forbidExtMatch = true;
	magic          = ["Rumble Fighter game data archive", /^geArchive: NSZ_NSZJ?( |$)/];
	converters     = ["gameextractor[codes:NSZ_NSZJ,NSZ_NSZ]"];
}
