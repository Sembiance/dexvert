import {Format} from "../../Format.js";

export class atr extends Format
{
	name          = "Atari ATR Floppy Disk Image";
	website       = "http://fileformats.archiveteam.org/wiki/ATR";
	ext           = [".atr"];
	fileSize      = [92176, 133_136, 183_952];
	matchFileSize = true;
	magic         = ["Atari ATR disk image", "Atari ATR image"];
	notes         = "Several ATR disks (such as Rambrandt.ATR) don't seem to extract. Deark (and other ATR extraction tools) find them corrupted.";

	// Alternative: https://www.atarimax.com/jindroush.atari.org/asoft.html   (I got it compiled in sandbox/app/adir_src/
	// Alternative: https://github.com/robmcmullen/atrcopy
	converters = ["atr", "deark"];
}
