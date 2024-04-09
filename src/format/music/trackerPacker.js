import {Format} from "../../Format.js";

export class trackerPacker extends Format
{
	name         = "TrackerPacker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Trackerpacker_3_module";
	ext          = [".tp3", ".tp2", ".tp1"];
	magic        = ["Trackerpacker 3 Music", "Tracker Packer 1/2"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
