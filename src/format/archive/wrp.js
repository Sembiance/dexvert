import {xu} from "xu";
import {Format} from "../../Format.js";

export class wrp extends Format
{
	name           = "Warp Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/WRP";
	ext            = [".wrp"];
	forbidExtMatch = true;
	magic          = ["Warp compressed disk image"];
	converters     = ["unWRP"];
}
