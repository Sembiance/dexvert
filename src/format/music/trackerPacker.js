import {Format} from "../../Format.js";

export class trackerPacker extends Format
{
	name         = "TrackerPacker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Trackerpacker_3_module";
	ext          = [".tp3"];
	magic        = ["Trackerpacker 3 Music"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
