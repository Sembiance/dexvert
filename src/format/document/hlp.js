import {Format} from "../../Format.js";

export class hlp extends Format
{
	name    = "Windows Help File";
	website = "http://fileformats.archiveteam.org/wiki/HLP_(WinHelp)";
	ext     = [".hlp"];
	magic   = [
		"Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File", "MS Windows help Bookmark", "Windows 3.x Hilfedatei", "Windows 95/98 Hilfedatei", "Format: MS Help", "application/winhlp", /^MS Windows help annotation/,
		/^MS Windows 95 help/, /^fmt\/474( |$)/
	];
	idMeta  = ({macFileType, macFileCreator}) => macFileType==="HELP" && ["CRGR", "MSH2", "MSHE"].includes(macFileCreator);

	// UniExtract supports this format, but it just runs helpdeco behind the scenes, so we don't need to add that to the converters
	// deark also supports this, but just extracts the internal .shg files (also can output the raw text with a VERY EXPERIMENTAL option)
	converters = ["unHLPMVB[extractExtra]"];
}
