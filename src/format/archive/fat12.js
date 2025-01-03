import {Format} from "../../Format.js";

export class fat12 extends Format
{
	name           = "PC-98 FAT8/FAT12/FAT16";
	website        = "http://fileformats.archiveteam.org/wiki/FAT12";
	ext            = [".hdi", ".fdd", ".fdi", ".vhd"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;	// allow other more specialized formats like stDiskImage and rawPartition to take precedence
	magic          = ["PC-98 FAT8", "PC-98 FAT12", "PC-98 FAT16", "Anex86 PC98 floppy image", "Virtual Floppy Disk image"];
	converters     = ["pc98ripper", "uaeunp"];
}
