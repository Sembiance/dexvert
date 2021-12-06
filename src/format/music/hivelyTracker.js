import {Format} from "../../Format.js";

export class hivelyTracker extends Format
{
	name         = "Hively Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Hively_Tracker_module";
	ext          = [".hvl"];
	magic        = ["Hively Tracker module", "Hively Tracker Song"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
