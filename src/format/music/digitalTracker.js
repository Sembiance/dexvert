import {Format} from "../../Format.js";

export class digitalTracker extends Format
{
	name         = "Digital Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Digital_Tracker_module";
	ext          = [".dtm"];
	magic        = ["Digital Tracker 1.9 module", /^Digital Tracker \d-channel module$/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
