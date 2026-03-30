import {xu} from "xu";
import {Format} from "../../Format.js";

export class oricDisk extends Format
{
	name           = "ORIC Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/DSK_(Oric)";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Oric Image", "Oric disk image", "Oric MFM disk image"];
	converters     = ["unORICDisk"];
}
