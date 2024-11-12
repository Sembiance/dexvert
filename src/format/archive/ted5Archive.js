import {Format} from "../../Format.js";

export class ted5Archive extends Format
{
	name        = "TED5 Archive";
	website     = "https://moddingwiki.shikadi.net/wiki/TED5";
	ext         = [".wl1", ".ck4", ".ck6"];
	magic       = ["GameMaps format", "Format: GameMaps (TED editor)"];
	unsupported = true;
	notes       = "An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.";
}
