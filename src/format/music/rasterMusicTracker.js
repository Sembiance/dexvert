import {Format} from "../../Format.js";

export class rasterMusicTracker extends Format
{
	name         = "RASTER Music Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/RASTER_Music_Tracker_module";
	ext          = [".rmt"];
	magic        = ["RASTER Music Tracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "asapconv"];
}
