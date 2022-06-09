import {Format} from "../../Format.js";

export class ensoniqDiskImage extends Format
{
	name           = "Ensoniq Disk Image";
	ext            = [".gkh", ".eds", ".eda", ".ede", ".edt", ".edv"];
	forbidExtMatch = true;
	magic          = [/^Ensoniq .*disk image/];
	converters     = ["awaveStudio"];
}
