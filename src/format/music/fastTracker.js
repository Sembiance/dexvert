import {Format} from "../../Format.js";

export class fastTracker extends Format
{
	name         = "FastTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/FastTracker_module";
	ext          = [".ft"];
	magic        = ["8-channel Fasttracker module sound data", "Fasttracker 8-channel Amiga Module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "xmp", "openmpt123"];
}
