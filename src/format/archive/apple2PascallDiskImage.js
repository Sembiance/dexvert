import {Format} from "../../Format.js";

export class apple2PascallDiskImage extends Format
{
	name           = "Apple II Pascal Disk Image";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Apple II Pascal disk image", "Apple Pascal Image"];
	converters     = ["acx"];
}
