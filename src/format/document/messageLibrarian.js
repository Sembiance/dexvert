import {Format} from "../../Format.js";

export class messageLibrarian extends Format
{
	name           = "Novell/C-Worthy Message Librarian";
	ext            = [".msg", ".dat"];
	forbidExtMatch = true;
	magic          = [/^Novell [Mm]essage [Ll]ibrarian [Dd]ata/, "C-Worthy Message Librarian Data"];
	converters     = ["strings"];
}
