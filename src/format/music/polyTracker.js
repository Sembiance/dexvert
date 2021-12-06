import {Format} from "../../Format.js";

export class polyTracker extends Format
{
	name         = "Poly Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Poly_Tracker_module";
	ext          = [".ptm"];
	magic        = ["Poly Tracker PTM Module", "Poly Tracker Module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
