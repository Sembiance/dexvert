import {Format} from "../../Format.js";

export class fashionTracker extends Format
{
	name         = "Fashion Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Fashion_Tracker_module";
	ext          = [".ex"];
	magic        = ["Fashion Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
