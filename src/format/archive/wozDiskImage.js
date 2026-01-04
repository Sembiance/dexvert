import {Format} from "../../Format.js";

export class wozDiskImage extends Format
{
	name       = "WOZ disk image";
	website    = "http://fileformats.archiveteam.org/wiki/WOZ";
	ext        = [".woz"];
	magic      = ["WOZ disk image", /^Apple ]\[ WOZ .*Disk Image/];
	converters = ["acx"];
}
