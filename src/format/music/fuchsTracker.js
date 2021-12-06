import {Format} from "../../Format.js";

export class fuchsTracker extends Format
{
	name         = "Fuchs Tracker module";
	website      = "http://fileformats.archiveteam.org/wiki/Fuchs_Tracker";
	ext          = [".fuchs", ".ft"];
	magic        = ["Fuchs Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
