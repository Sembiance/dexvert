import {Format} from "../../Format.js";

export class realityTracker extends Format
{
	name         = "Reality AdLib Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Reality_AdLib_Tracker_module";
	ext          = [".rad"];
	magic        = ["Reality Adlib Tracker module", "RAD Adlib Tracker Module RAD"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
