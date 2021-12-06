import {Format} from "../../Format.js";

export class extremeTracker extends Format
{
	name         = "Extreme's Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Extreme%27s_Tracker_module";
	ext          = [".ams"];
	magic        = ["Extreme Tracker AMS Module", "Extreme's Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
