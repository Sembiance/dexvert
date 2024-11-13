import {Format} from "../../Format.js";

export class fastTracker extends Format
{
	name         = "FastTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/FastTracker_module";
	ext          = [".ft"];
	magic        = [/\d-channel Fasttracker module sound data/, /Fasttracker \d-channel Amiga Module/, "FlexTrax module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "xmp", "openmpt123"];
}
