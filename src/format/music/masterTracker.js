import {Format} from "../../Format.js";

export class masterTracker extends Format
{
	name        = "Master Tracker AdLib Module";
	website     = "http://fileformats.archiveteam.org/wiki/Master_Tracker_module";
	ext         = [".mtr"];
	magic       = ["Master Tracker Ad Lib module", "Master Tracker module"];
	weakMagic   = ["Master Tracker module"];
	unsupported = true;
}
