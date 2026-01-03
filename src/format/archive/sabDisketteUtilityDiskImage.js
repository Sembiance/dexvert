import {Format} from "../../Format.js";

export class sabDisketteUtilityDiskImage extends Format
{
	name           = "SAB Diskette Utility disk image";
	website        = "http://fileformats.archiveteam.org/wiki/SABDU";
	ext            = [".sdu"];
	forbidExtMatch = true;
	magic          = ["SAB Diskette Utility disk image"];
	converters     = ["dd[bs:46][skip:1] -> dexvert"];
}
