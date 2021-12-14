import {Format} from "../../Format.js";

export class textPlus extends Format
{
	name           = "Text Plus Document";
	ext            = [".txp"];
	forbidExtMatch = true;
	magic          = ["Text Plus document"];
	converters     = ["strings"];
}
