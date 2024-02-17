import {Format} from "../../Format.js";

export class xar extends Format
{
	name       = "eXtensible ARchive";
	website    = "http://fileformats.archiveteam.org/wiki/Xar_(Extensible_Archive)";
	ext        = [".xar"];
	magic      = ["xar archive compressed", "XAR Archive", /^XAR$/, /^fmt\/600( |$)/];
	converters = ["xar", "unar"];
}
