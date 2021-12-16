import {Format} from "../../Format.js";

export class vendinfo extends Format
{
	name           = "VENDINFO";
	ext            = [".diz"];
	forbidExtMatch = true;
	magic          = ["VENDINFO information"];
	filename       = [/^vendinfo\.diz$/i];
	untouched      = true;
	metaProvider   = ["text"];
}
