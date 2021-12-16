import {Format} from "../../Format.js";

export class neoBookDocument extends Format
{
	name           = "NeoBook Document";
	ext            = [".pub"];
	forbidExtMatch = true;
	magic          = ["NeoBook for DOS document"];
	untouched      = true;
	metaProvider   = ["text"];
}
