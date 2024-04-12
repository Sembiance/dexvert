import {Format} from "../../Format.js";

export class adfFFS extends Format
{
	name          = "Amiga Disk Format (FFS)";
	website       = "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)";
	ext           = [".adf"];
	fileSize      = 901_120;
	matchFileSize = true;
	magic         = ["Amiga Disk image File (FFS", "Amiga FFS disk", "Amiga Inter FFS disk", "Amiga Fastdir FFS disk", "Amiga FFS file system"];
	converters    = ["unadf", "uaeunp", "xdftool"];
}
