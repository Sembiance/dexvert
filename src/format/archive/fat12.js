import {Format} from "../../Format.js";

export class fat12 extends Format
{
	name           = "FAT12";
	ext            = [".hdi", ".fdd", ".fdi"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;	// allow other more specialized formats like stDiskImage and rawPartition to take precedence
	magic          = ["PC-98 FAT12", "Anex86 PC98 floppy image"];
	converters     = ["pc98ripper", "uaeunp"];
}
