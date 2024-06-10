import {Format} from "../../Format.js";

export class dietDisk extends Format
{
	name       = "DietDisk Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/Diet_Disk";
	magic      = ["LZDiet compressed data"];
	packed     = true;
	converters = ["dietDiskFatten"];
}
