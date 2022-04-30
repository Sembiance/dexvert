import {Format} from "../../Format.js";

export class xz extends Format
{
	name       = "XZ Archive";
	website    = "http://fileformats.archiveteam.org/wiki/XZ";
	ext        = [".xz"];
	magic      = ["XZ compressed data", "xz compressed container"];
	packed     = true;
	converters = ["xz", "sevenZip", "unar", "UniExtract"];
}
