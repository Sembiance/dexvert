import {Format} from "../../Format.js";

export class fdcopyCFI extends Format
{
	name       = "FDCOPY.COM CFI Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/CFI_disk_image";
	ext        = [".cfi"];
	converters = ["dskconv[inType:cfi]"];
}
