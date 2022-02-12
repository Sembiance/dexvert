import {Format} from "../../Format.js";

export class amusicTracker extends Format
{
	name         = "AMUSIC Adlib Tracker";
	ext          = [".amd"];
	magic        = ["Amusic tracker"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
