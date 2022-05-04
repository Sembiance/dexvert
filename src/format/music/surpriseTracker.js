import {Format} from "../../Format.js";

export class surpriseTracker extends Format
{
	name         = "Surprise! AdLib Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Surprise!_Adlib_Tracker_v2.0";
	ext          = [".sat", ".sa2"];
	magic        = ["Surprise! Adlib Tracker", "Surprise! AdLib Tracker", /^fmt\/1552( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
