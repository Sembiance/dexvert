import {Format} from "../../Format.js";

export class monkeyIsland3Archive extends Format
{
	name           = "Monkey Island 3 Archive";
	ext            = [".bun"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BUN_LB83( |$)/, "dragon: BUN "];
	converters     = ["gameextractor[codes:BUN_LB83]", "dragonUnpacker[types:BUN]"];
}
