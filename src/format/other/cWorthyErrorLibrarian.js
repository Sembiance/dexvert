import {Format} from "../../Format.js";

export class cWorthyErrorLibrarian extends Format
{
	name           = "C-Worthy Error Librarian Data";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["C-Worthy Error Librarian Data"];
	converters     = ["strings"];
}
