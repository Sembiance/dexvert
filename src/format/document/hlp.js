import {Format} from "../../Format.js";

export class hlp extends Format
{
	name       = "Windows Help File";
	website    = "http://fileformats.archiveteam.org/wiki/HLP";
	ext        = [".hlp"];
	magic      = ["Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File"];
	converters = ["hlp2pdf", "UniExtract"];
}
