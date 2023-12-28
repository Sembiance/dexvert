import {Format} from "../../Format.js";

export class disorderTracker extends Format
{
	name         = "Disorder Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/DisorderTracker_2_module";
	ext          = [".plm"];
	magic        = ["Disorder Tracker 2 module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
