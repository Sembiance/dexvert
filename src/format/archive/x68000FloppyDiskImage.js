import {Format} from "../../Format.js";

export class x68000FloppyDiskImage extends Format
{
	name       = "X68000 Floppy Disk Image";
	ext        = [".xdf"];
	magic      = ["X68000 Floppy Disk image"];
	converters = ["uniso"];
}
