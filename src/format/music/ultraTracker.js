import {Format} from "../../Format.js";

export class ultraTracker extends Format
{
	name         = "Ultra Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Ultra_Tracker";
	ext          = [".ult"];
	magic        = [/^ultratracker .*module sound data$/i, "Ultra Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123", "xmp"];
}
