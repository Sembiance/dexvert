import {Format} from "../../Format.js";

export class cpcDisk extends Format
{
	name       = "Amstrad CPC Disk";
	website    = "http://fileformats.archiveteam.org/wiki/DSK_(CPCEMU)";
	ext        = [".dsk"];
	magic      = ["Extended CPCEMU style disk image", "Amstrad/Spectrum Extended .DSK data"];
	converters = ["cpcxfs"];
}
