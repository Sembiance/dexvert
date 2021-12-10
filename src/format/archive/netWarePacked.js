import {Format} from "../../Format.js";

export class netWarePacked extends Format
{
	name       = "Novel NetWare Packed File";
	website    = "http://fileformats.archiveteam.org/wiki/NetWare_Packed_File";
	magic      = ["Personal NetWare Packed File", "Novell Packed data"];
	converters = ["nwunpack"];
}
