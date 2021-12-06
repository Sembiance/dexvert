import {Format} from "../../Format.js";

export class impulseTracker extends Format
{
	name         = "Impulse Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Impulse_Tracker_module";
	ext          = [".it"];
	magic        = ["Impulse Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
