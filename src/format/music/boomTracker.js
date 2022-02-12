import {Format} from "../../Format.js";

export class boomTracker extends Format
{
	name         = "Boom Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Boom_Tracker_v4.0_module";
	ext          = [".cff"];
	magic        = ["BoomTracker", "CFF Song"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
