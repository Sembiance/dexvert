import {Format} from "../../Format.js";

export class krisChipTracker extends Format
{
	name         = "Kris/Chip Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/KRIS_Packer_/_ChipTracker_module";
	ext          = [".kris"];
	magic        = ["Kris Tracker / ChipTracker song/module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
