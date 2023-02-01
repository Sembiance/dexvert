import {Format} from "../../Format.js";

export class diskDupeDiskImage extends Format
{
	name       = "DiskDupe Disk Image";
	ext        = [".ddi"];
	magic      = ["DiskDupe Disk Image"];
	converters = ["sevenZip"];
}
