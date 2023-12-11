import {Format} from "../../Format.js";

export class apriDisk extends Format
{
	name           = "ApriDisk";
	website        = "http://fileformats.archiveteam.org/wiki/ApriDisk";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["ACT Apricot disk image"];
	unsupported    = true;
	notes          = "The apridisk.exe program can write these to a real floppy, so maybe I could use DOSBOX and an inserted blank floppy to try and write these and then convert, but meh.";
}
