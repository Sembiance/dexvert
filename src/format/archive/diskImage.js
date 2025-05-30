import {Format} from "../../Format.js";

export class diskImage extends Format
{
	name    = "Disk Image";
	website = "http://fileformats.archiveteam.org/wiki/Raw_disk_image";
	ext     = [".img", ".dsk", ".flp"];
	weakExt = true;
	magic   = [
		// generic
		"Generic PC disk image", "FAT Disk Image", "DOS floppy", "Old DOS disk image",  "BeOS boot loader",
		/^fmt\/1087( |$)/,
		
		// specific
		"Distribution Media Format disk image", "DoubleSpace compressed volume (v6.0)", "CP Backup disk image", "2FILE disk image"
	];

	// 7z isn't a very reliable program with unknown data, so if we've only matched on extension, lower our confidence a lot so other format families like images have a chance
	confidenceAdjust = (inputFile, matchType) => (matchType==="ext" ? -20 : 0);
	
	converters = ["sevenZip", "aaru[matchType:magic][strongMatch]"];
}
