import {Format} from "../../Format.js";

export class krisChipTracker extends Format
{
	name         = "Kris/Chip Tracker Module";
	ext          = [".kris"];
	magic        = ["Kris Tracker / ChipTracker song/module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
