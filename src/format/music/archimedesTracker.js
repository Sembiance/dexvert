import {Format} from "../../Format.js";

export class archimedesTracker extends Format
{
	name         = "Archimedes Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Archimedes_Tracker_module";
	ext          = [".musx"];
	magic        = ["MusX Archimedes Tracker module", /^fmt\/1473( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
