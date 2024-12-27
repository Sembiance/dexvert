import {Format} from "../../Format.js";

export class mameCHD extends Format
{
	name       = "MAME Compressed Hard Disk image";
	website    = "https://www.psxdev.net/forum/viewtopic.php?t=3980";
	ext        = [".chd", ".hd"];
	magic      = ["MAME Compressed Hard Disk image", "application/x-mame-chd", /^MAME CHD compressed hard disk image/];
	converters = ["chdman"];
}
