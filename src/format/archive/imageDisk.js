import {Format} from "../../Format.js";

export class imageDisk extends Format
{
	name           = "ImageDisk Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/IMD";
	ext            = [".imd"];
	forbidExtMatch = true;
	magic          = ["ImageDisk disk image"];
	converters     = ["dskconv[inType:imd]"];
}
