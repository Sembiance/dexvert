import {Format} from "../../Format.js";

export class firstChoiceDatabase extends Format
{
	name           = "First Choice Database";
	ext            = [".fol", ".pfs"];
	forbidExtMatch = true;
	magic          = ["First Choice database"];
	weakMagic      = true;
	converters     = ["strings"];
}
