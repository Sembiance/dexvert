import {Format} from "../../Format.js";

export class pumaTracker extends Format
{
	name         = "Puma Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Pumatracker_module";
	ext          = [".puma"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
