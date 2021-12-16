import {Format} from "../../Format.js";

export class gnuBisonGrammar extends Format
{
	name           = "GNU Bison Grammar";
	ext            = [".yy", ".y"];
	forbidExtMatch = true;
	magic          = ["GNU Bison grammar"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
