import {Format} from "../../Format.js";

export class amusicTrackerXMS extends Format
{
	name         = "AMUSIC Adlib Tracker XMS";
	website      = "http://fileformats.archiveteam.org/wiki/AMusic_XMS";
	ext          = [".xms"];
	magic        = ["XMS Adlib Module Composer", "XMS-Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
