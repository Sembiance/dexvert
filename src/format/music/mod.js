import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class mod extends Format
{
	name           = "Protracker Module";
	website        = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext            = [".mod", ".ptm", ".pt36"];
	magic          = [/.*Protracker module/, "Standard 4-channel Amiga module", "ProTracker IFF module"];
	forbiddenMagic = TEXT_MAGIC;
	metaProvider   = ["musicInfo"];
	converters     = dexState =>
	{
		const a = ["xmp", "uade123", "mikmod2wav", "zxtune123"];

		// awaveStudio isn't safe to use for this format all willy nilly, so only use it if we are a magic match
		if(dexState.id.matchType==="magic")
			a.push("awaveStudio");

		return a;
	};
}
