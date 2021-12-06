import {Format} from "../../Format.js";

export class graoumfTracker extends Format
{
	name        = "Graoumf Tracker Module";
	website     = "http://fileformats.archiveteam.org/wiki/Graoumf_Tracker_module";
	ext         = [".gtk", ".gt2"];
	magic       = ["Graoumf Tracker module", "Graoumf Tracker 2 module"];
	unsupported = true;
	notes       = "Could probably add support with windows Graoumf Tracker: http://graoumftracker2.sourceforge.net/";
}
