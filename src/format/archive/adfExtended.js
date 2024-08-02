import {Format} from "../../Format.js";

export class adfExtended extends Format
{
	name           = "Amiga Disk Format Extended";
	ext            = [".adf"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	magic          = ["EXT2 Extended Amiga Disk image File"];
	converters     = ["uaeunp -> dexvert"];
}
