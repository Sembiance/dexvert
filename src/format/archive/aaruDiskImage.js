import {Format} from "../../Format.js";

export class aaruDiskImage extends Format
{
	name       = "Aaru Disk Image";
	website    = "https://github.com/aaru-dps/Aaru";
	ext        = [".aaru", ".aaruf", ".aaruformat", ".dicf"];
	magic      = ["Aaru disk image"];
	converters = ["aaru"];
}
