import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class mod extends Format
{
	name           = "Protracker Module";
	website        = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext            = [".mod", ".ptm", ".pt36", ".wow"];
	weakExt        = [".mod", ".wow"];	// .mod too generic, let music/soundTracker grab it   .wow belongs to Mod's Grave
	magic          = [/.*Protracker module/, "Standard 4-channel Amiga module", "ProTracker IFF module", /^fmt\/716( |$)/];
	idMeta         = ({macFileType}) => macFileType==="STrk";
	forbiddenMagic = TEXT_MAGIC_STRONG;
	metaProvider   = ["musicInfo"];
	converters     = ["xmp", "uade123", "mikmod2wav", "zxtune123", "awaveStudio[matchType:magic]"];	// not sure whey openmpt123 isn't listed here, but it must have been on purpose
}
