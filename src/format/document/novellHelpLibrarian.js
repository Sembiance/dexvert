import {Format} from "../../Format.js";

export class novellHelpLibrarian extends Format
{
	name           = "Novell Help Librarian";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Novell Help Librarian Data"];
	converters     = ["strings"];
}
