import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class mod extends Format
{
	name           = "Protracker Module";
	website        = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext            = [".mod", ".ptm", ".pt36"];
	weakExt        = [".mod"];	// too generic, let music/soundTracker grab it
	magic          = [/.*Protracker module/, "Standard 4-channel Amiga module", "ProTracker IFF module"];
	forbiddenMagic = TEXT_MAGIC_STRONG;
	metaProvider   = ["musicInfo"];
	converters     = ["xmp", "uade123", "mikmod2wav", "zxtune123", "awaveStudio[matchType:magic]"];
}
