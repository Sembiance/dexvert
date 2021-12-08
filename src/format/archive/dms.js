import {Format} from "../../Format.js";

export class dms extends Format
{
	name       = "Amiga Disk Master System Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Disk_Masher_System";
	ext        = [".dms", ".fms"];
	magic      = ["Disk Masher System compressed disk image", "DMS archive data"];
	converters = ["unar[renameOut]"];
}
