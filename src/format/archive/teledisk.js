import {Format} from "../../Format.js";

export class teledisk extends Format
{
	name        = "Teledisk Disk Image";
	website     = "http://fileformats.archiveteam.org/wiki/TD0";
	ext         = [".td0"];
	magic       = ["Teledisk Disk compressed image", "floppy image data (TeleDisk)"];
	unsupported = true;
}
