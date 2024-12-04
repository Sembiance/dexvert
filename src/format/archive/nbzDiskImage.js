import {Format} from "../../Format.js";

export class nbzDiskImage extends Format
{
	name       = "C64 NBZ Disk Image";
	website    = "https://c64preservation.com/dp.php?pg=nibtools";
	ext        = [".nbz"];
	magic      = ["C64 NBZ disk image"];
	converters = ["nibconv"];
}
