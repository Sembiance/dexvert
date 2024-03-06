import {Format} from "../../Format.js";

export class dms extends Format
{
	name       = "Amiga Disk Master System Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Disk_Masher_System";
	ext        = [".dms", ".fms"];
	magic      = ["Disk Masher System compressed disk image", "DMS archive data", "DMS: Disk Masher System", /^DMS$/];
	packed     = true;
	converters = ["uaeunp", "unar[filenameEncoding:iso-8859-1]", "ancient"];	// uaeunp picks up certain extra files like Banners and FILE_ID.DIZ files and can brute-force encrypted DMS files
}
