import {Format} from "../../Format.js";

export class soundTrackerProII extends Format
{
	name         = "Soundtracker Pro II Module";
	ext          = [".stp"];
	magic        = ["Spectrum Sound Tracker Pro 2 chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
