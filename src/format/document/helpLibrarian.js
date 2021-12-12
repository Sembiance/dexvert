import {Format} from "../../Format.js";

export class helpLibrarian extends Format
{
	name           = "Help Librarian Help File";
	website        = "http://fileformats.archiveteam.org/wiki/Help_Librarian";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["C-Worthy Help Librarian Data"];
	converters     = ["strings"];
}
