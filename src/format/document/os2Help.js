import {Format} from "../../Format.js";

export class os2Help extends Format
{
	name           = "OS/2 Help File";
	website        = "http://fileformats.archiveteam.org/wiki/INF/HLP_(OS/2)";
	ext            = [".hlp", ".inf"];
	forbidExtMatch = true;
	magic          = ["OS/2 HLP", "OS/2 Help", "OS/2 Information Presentation Facility", "OS/2 INF", "Format: OS/2 help file"];
	notes          = "The ipf2txt file is limited on what files it can convert due to 16-bit limitations.";
	converters     = ["ipf2txt"];
}
