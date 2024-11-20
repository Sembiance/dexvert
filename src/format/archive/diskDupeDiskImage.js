import {Format} from "../../Format.js";

export class diskDupeDiskImage extends Format
{
	name       = "DiskDupe Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/DDI";
	ext        = [".ddi"];
	magic      = ["DiskDupe Disk Image", "DiskDupe/MSD Disk Image"];
	converters = ["sevenZip"];
}
