import {Format} from "../../Format.js";

export class hlp extends Format
{
	name       = "Windows Help File";
	website    = "http://fileformats.archiveteam.org/wiki/HLP";
	ext        = [".hlp"];
	magic      = ["Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File", /^fmt\/474( |$)/];
	converters = ["unHLPMVB"];	// UniExtract supports this format, but it just runs helpdeco behind the scenes, so we don't need to add that to the converters
}
