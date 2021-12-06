import {Format} from "../../Format.js";

export class madTracker extends Format
{
	name         = "MadTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/MadTracker_2_module";
	ext          = [".mt2"];
	magic        = ["MadTracker 2 module", "MadTracker 2.0 Module"];
	notes        = "Sample file a little rock/mt2 doesn't convert";
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
