import {Format} from "../../Format.js";

export class starbreezeStudiosGameDataArchive extends Format
{
	name           = "Starbreeze Studios game data archive";
	ext            = [".xw", ".xfc", ".xtc", ".xcd", ".xwc"];
	forbidExtMatch = true;
	magic          = ["Starbreeze Studios game data archive", /^geArchive: XWC_MOS( |$)/, "dragon: MOSD "];
	converters     = ["gameextractor[codes:XWC_MOS]", "dragonUnpacker[types:MOSD]"];
}
