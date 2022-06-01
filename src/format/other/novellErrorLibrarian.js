import {Format} from "../../Format.js";

export class novellErrorLibrarian extends Format
{
	name           = "Novell Error Librarian";
	ext            = [".dat", ".idx"];
	forbidExtMatch = true;
	magic          = ["Novell Error Librarian Data"];
	converters     = ["strings"];
}
