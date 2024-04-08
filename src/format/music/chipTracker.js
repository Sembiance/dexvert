import {Format} from "../../Format.js";

export class chipTracker extends Format
{
	name         = "Chip Tracker Module";
	website      = "http://bzrplayer.blazer.nu/fileformat/chip-tracker/76";
	ext          = [".chi", ".mod"];
	weakExt      = [".mod"];
	magic        = ["Chip Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
