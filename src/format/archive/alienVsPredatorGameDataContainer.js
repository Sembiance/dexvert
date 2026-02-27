import {Format} from "../../Format.js";

export class alienVsPredatorGameDataContainer extends Format
{
	name           = "Alien vs Predator game data container";
	ext            = [".ffl"];
	forbidExtMatch = true;
	magic          = ["Alien vs Predator game data container", /^geArchive: FFL_RFFL( |$)/, "dragon: RFFL "];
	converters     = ["gameextractor[codes:FFL_RFFL]", "dragonUnpacker[types:RFFL]"];
}
