import {Format} from "../../Format.js";

export class surpriseTracker extends Format
{
	name         = "Surprise! AdLib Tracker";
	ext          = [".sat", ".sa2"];
	magic        = ["Surprise! Adlib Tracker", "Surprise! AdLib Tracker"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
