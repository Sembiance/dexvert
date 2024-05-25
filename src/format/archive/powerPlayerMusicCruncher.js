import {Format} from "../../Format.js";

export class powerPlayerMusicCruncher extends Format
{
	name       = "PowerPlayer Music Cruncher";
	magic      = ["PowerplayerMusic Cruncher", "Archive: PowerPlayer Music Cruncher"];
	packed     = true;
	converters = ["xfdDecrunch"];
}
