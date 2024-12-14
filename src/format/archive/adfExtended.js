import {Format} from "../../Format.js";

export class adfExtended extends Format
{
	name           = "Amiga Disk Format Extended";
	website        = "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)";
	ext            = [".adf"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	magic          = [/^EXT\d Extended Amiga Disk image File/];
	converters     = ["uaeunp -> dexvert"];
}
