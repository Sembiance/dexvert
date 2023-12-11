import {Format} from "../../Format.js";

export class copyQMDiskImage extends Format
{
	name           = "CopyQM Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/CopyQM";
	ext            = [".cqm"];
	forbidExtMatch = true;
	magic          = ["CopyQM disk image", /^floppy image data.+CopyQM/];
	converters     = ["dskconv[inType:copyqm]"];
}
