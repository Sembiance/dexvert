import {Format} from "../../Format.js";

export class vipPhonebook extends Format
{
	name           = "V.I.P. Phonebook";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["V.I.P. phonebook data"];
	converters     = ["strings"];
}
