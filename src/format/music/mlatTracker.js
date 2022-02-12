import {Format} from "../../Format.js";

export class mlatTracker extends Format
{
	name         = "Mlat Tracker";
	ext          = [".mad"];
	magic        = ["Mlat Ad Lib Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
