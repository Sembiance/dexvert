import {Format} from "../../Format.js";

export class impulseTrackerSample extends Format
{
	name       = "Impulse Tracker Sample";
	website    = "http://fileformats.archiveteam.org/wiki/Impulse_Tracker_sample";
	ext        = [".its"];
	magic      = ["Impulse Tracker Sample"];
	converters = ["awaveStudio"];
}
