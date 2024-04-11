import {Format} from "../../Format.js";

export class xm extends Format
{
	name         = "Extended Module";
	website      = "http://fileformats.archiveteam.org/wiki/Extended_Module";
	ext          = [".xm", ".oxm"];
	magic        = ["Fasttracker II module sound data", "FastTracker 2 eXtended Module", /^fmt\/323( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
