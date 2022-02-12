import {Format} from "../../Format.js";

export class realityTracker extends Format
{
	name         = "Reality AdLib Tracker";
	ext          = [".rad"];
	magic        = ["Reality Adlib Tracker module", "RAD Adlib Tracker Module RAD"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
