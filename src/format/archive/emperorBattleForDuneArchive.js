import {Format} from "../../Format.js";

export class emperorBattleForDuneArchive extends Format
{
	name           = "Emperor Battle for Dune Archive";
	ext            = [".bag"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BAG_GABA( |$)/, "dragon: BAG "];
	converters     = ["dragonUnpacker[types:BAG]", "gameextractor[codes:BAG_GABA]"];
}
