import {Format} from "../../Format.js";

export class relicChunkyContainerGameData extends Format
{
	name           = "Relic Chunky container - game data";
	ext            = [".sgb", ".whm", ".whe", ".rsh", ".wtp"];
	forbidExtMatch = true;
	magic          = ["Relic Chunky container - game data", /^geArchive: RSH_RELICCHUNKY( |$)/];
	converters     = ["gameextractor[codes:RSH_RELICCHUNKY]"];
	unsupported    = true;
	notes          = "Over 200,000 of these on discmaster and they don't appear to extract into any files that can be acted upon, so just skip this";
}
