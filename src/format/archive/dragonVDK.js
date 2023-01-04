import {Format} from "../../Format.js";

export class dragonVDK extends Format
{
	name       = "Dragon DOS VDK Disk Image";
	website    = "http://archive.worldofdragon.org/index.php?title=Tape%5CDisk_Preservation#VDK_File_Format";
	ext        = [".vdk"];
	magic      = ["Dragon VDK Disk image format"];
	converters = ["dcopy"];
}
