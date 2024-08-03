import {Format} from "../../Format.js";

export class amigaHardDiskPFS extends Format
{
	name        = "Amiga Hard Disk Image (PFS)";
	ext         = [".hdf", ".adf"];
	magic       = ["Amiga hard disk image (PFS)", "Amiga PFS file system"];
	unsupported = true;
	notes       = "Have not found a linux extractor for this format yet.";
}
