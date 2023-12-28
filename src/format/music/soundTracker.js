import {Format} from "../../Format.js";

export class soundTracker extends Format
{
	name         = "SoundTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Soundtracker_v2.6_/_Ice_Tracker_module";
	ext          = [".mod", ".st26"];
	matchPreExt  = true;
	//priority     = this.PRIORITY.LOW;
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "uade123", "zxtune123", "openmpt123"];
}
