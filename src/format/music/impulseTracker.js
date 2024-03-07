import {Format} from "../../Format.js";

export class impulseTracker extends Format
{
	name         = "Impulse Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Impulse_Tracker_module";
	ext          = [".it"];
	magic        = ["Impulse Tracker module", "Impulse Tracker Modul", /^fmt\/715( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
