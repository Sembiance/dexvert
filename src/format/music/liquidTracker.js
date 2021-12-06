import {Format} from "../../Format.js";

export class liquidTracker extends Format
{
	name         = "Liquid Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Liquid_Tracker_module";
	ext          = [".liq"];
	magic        = ["Liquid Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
