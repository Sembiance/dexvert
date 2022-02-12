import {Format} from "../../Format.js";

export class amusicTracker extends Format
{
	name         = "AMUSIC Adlib Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/AMusic_module";
	ext          = [".amd"];
	magic        = ["Amusic tracker"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
