import {Format} from "../../Format.js";

export class sgml extends Format
{
	name           = "SGML Document";
	ext            = [".sgml"];
	forbidExtMatch = true;
	magic          = ["exported SGML document", "HyperText Markup Language"];
	weakMagic      = true;
	untouched      = true;
}
