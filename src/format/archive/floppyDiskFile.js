import {Format} from "../../Format.js";

export class floppyDiskFile extends Format
{
	name           = "Floppy Disk File";
	ext            = [".fdf"];
	forbidExtMatch = true;
	magic          = ["Floppy Disk File image"];
	converters     = ["vibeExtract[singleFile][renameOut] -> dexvert"];
}
