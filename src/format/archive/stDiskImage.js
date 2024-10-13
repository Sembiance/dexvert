import {Format} from "../../Format.js";

export class stDiskImage extends Format
{
	name       = "Atari ST Floppy Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/ST_disk_image";
	ext        = [".st"];
	magic      = ["Atari-ST floppy", "Atari-ST Minix kernel image, 360k floppy"];
	converters = ["uniso[checkMount]"];
}
