import {xu} from "xu";
import {Format} from "../../Format.js";

export class adfOFS extends Format
{
	name          = "Amiga Disk Format (OFS)";
	website       = "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)";
	ext           = [".adf"];
	fileSize      = 901_120;
	matchFileSize = true;
	magic         = ["Amiga Disk image File (OFS", "Amiga DOS disk", /^fmt\/1361( |$)/];
	notes         = xu.trim`
		Some Amiga disks (such as voyager.adf) are non DOS (NDOS) disks with custom filesystems.
		Others are crazy corrupted and produce lots of really bad files, such as 117.adf
		These cannot be mounted by the amiga nor extracted with unar/unadf/adf-extractor
		These are custom disk formats that demo and game coders came up with to squeeze data out of em.
		Sadly there isn't really any way to extract files from these disks, as they might not even have a concept of files at all.`;
	
	converters =  ["unar[filenameEncoding:iso-8859-1]", "uaeunp", "unadf", "extract_adf"];	// unadf handles files better, but doesn't preserve all timestamps? unar preserves timestamps well.
}
