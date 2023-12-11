import {xu} from "xu";
import {Format} from "../../Format.js";

export class oricDisk extends Format
{
	name           = "ORIC Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/DSK_(Oric)";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Oric Image", "Oric disk image", "Oric MFM disk image"];
	unsupported    = true;
	notes          = "The sandbox/app/oric-dsk-manager Java program can extract these files, but I couldn't get it to run under linux, so meh.";
}
