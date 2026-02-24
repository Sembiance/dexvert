import {Format} from "../../Format.js";

export class stardockEntertainmentGameDataArchive extends Format
{
	name           = "Stardock Entertainment game data archive";
	ext            = [".emp", ".mtd"];
	forbidExtMatch = true;
	magic          = ["Stardock Entertainment game data archive", /^geArchive: MTD_MTDLIB( |$)/];
	converters     = ["gameextractor[codes:MTD_MTDLIB]"];
}
