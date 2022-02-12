import {Format} from "../../Format.js";

export class adLibTracker2 extends Format
{
	name         = "AdLib Tracker 2";
	ext          = [".a2m"];
	magic        = ["A2M Song", "AdLib Tracker II Module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
