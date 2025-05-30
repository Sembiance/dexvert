import {Format} from "../../Format.js";

export class adfFFS extends Format
{
	name          = "Amiga Disk Format (FFS)";
	website       = "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)";
	ext           = [".adf"];
	fileSize      = 901_120;
	matchFileSize = true;
	magic         = ["Amiga Disk image File (FFS", "Amiga FFS", "Amiga Inter FFS", "Amiga Fastdir FFS", "Amiga FFS file system", "deark: amiga_adf (Amiga ADF, FFS)"];
	converters    = ["unadf", "uaeunp", "xdftool"];
}
