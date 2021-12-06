import {Format} from "../../Format.js";

export class funkTracker extends Format
{
	name         = "FunkTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/FunkTracker_module";
	ext          = [".fnk"];
	magic        = ["FunkTracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
