import {Format} from "../../Format.js";

export class hlp extends Format
{
	name       = "Windows Help File";
	website    = "http://fileformats.archiveteam.org/wiki/HLP_(WinHelp)";
	ext        = [".hlp"];
	magic      = ["Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File", /^fmt\/474( |$)/];
	
	// UniExtract supports this format, but it just runs helpdeco behind the scenes, so we don't need to add that to the converters
	// deark also supports this, but just extracts the internal .shg files and that's it (also can output the raw text with a VERY EXPERIMENTAL option)
	converters = ["unHLPMVB[extractExtra]"];
}
