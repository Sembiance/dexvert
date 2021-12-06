import {Format} from "../../Format.js";

export class realTracker extends Format
{
	name         = "Real Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Real_Tracker_module";
	ext          = [".rtm"];
	magic        = ["Real Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
