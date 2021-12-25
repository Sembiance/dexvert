import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class starTracker extends Format
{
	name           = "Star Tracker/StarTrekker Module";
	website        = "http://fileformats.archiveteam.org/wiki/StarTrekker_/_Star_Tracker_module";
	ext            = [".mod"];
	weakExt        = [".mod"];	// too generic, let mod/soundTracker grab it
	magic          = [/^StarTrekker.* module$/, /Startracker module sound data/];
	forbiddenMagic = TEXT_MAGIC_STRONG;
	metaProvider   = ["musicInfo"];
	converters     = ["xmp", "zxtune123"];
}
