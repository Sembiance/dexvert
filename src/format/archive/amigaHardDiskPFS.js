import {Format} from "../../Format.js";

export class amigaHardDiskPFS extends Format
{
	name           = "Amiga Hard Disk Image (PFS)";
	ext            = [".hdf", ".adf"];
	forbidExtMatch = true;
	magic          = ["Amiga hard disk image (PFS)", "Amiga PFS file system"];
	converters     = ["unAmigaPFS"];
}
