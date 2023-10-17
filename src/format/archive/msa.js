import {Format} from "../../Format.js";

export class msa extends Format
{
	name       = "Magic Shadow Archiver";
	website    = "http://fileformats.archiveteam.org/wiki/MSA_(Atari)";
	ext        = [".msa"];
	magic      = ["Atari MSA archive data", "Atari MSA Disk Image", /^fmt\/1472( |$)/];
	notes      = "Unable to extract anything from adr_1.msa. The msa.exe program also fails to find any data. Yet a hex editor shows data. No other converters known.";
	
	// msa will convert to .st which I can then just mount and extract with uniso and preserves directory structure
	// deark works, but doesn't preserve directory structure at all
	converters = ["msa", "deark[module:msa]"];
}
