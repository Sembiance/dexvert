import {Format} from "../../Format.js";

export class m4 extends Format
{
	name           = "M4 Source File";
	ext            = [".m4"];
	forbidExtMatch = true;
	magic          = ["m4 preprocessor / macro source"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
