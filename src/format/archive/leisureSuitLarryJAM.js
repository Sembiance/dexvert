import {Format} from "../../Format.js";

export class leisureSuitLarryJAM extends Format
{
	name           = "Leisure Suit Larry JAM Archive";
	ext            = [".jam"];
	forbidExtMatch = true;
	magic          = [/^geArchive: JAM_JAM2( |$)/, "dragon: JAM2 "];
	converters     = ["dragonUnpacker[types:JAM2]", "gameextractor[codes:JAM_JAM2]"];
}
