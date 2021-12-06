import {Format} from "../../Format.js";

export class xm extends Format
{
	name         = "Extended Module";
	website      = "http://fileformats.archiveteam.org/wiki/XM";
	ext          = [".xm"];
	magic        = ["Fasttracker II module sound data", "FastTracker 2 eXtended Module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
