import {Format} from "../../Format.js";

export class hlp extends Format
{
	name       = "Windows Help File";
	website    = "http://fileformats.archiveteam.org/wiki/HLP";
	ext        = [".hlp"];
	magic      = ["Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File", /^fmt\/474( |$)/];
	// sometimes helpdeco crashes when writing the RTF file (sample file RETIREA.HLP) which leaves no files from hlp2pdf, so we just run helpdeco raw and see if it produces any files
	// UniExtract supports this format, but it just runs helpdeco behind the scenes, so we don't need to add that to the converters
	converters = ["hlp2pdf", "helpdeco"];
}
