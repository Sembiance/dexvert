import {Format} from "../../Format.js";

export class pcShrink extends Format
{
	name       = "PC-Shrink Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PC-Shrink";
	ext        = [".shr"];
	magic      = ["PC-Shrink compressed archive"];
	converters = ["deark[module:pcshrink]"];
}
