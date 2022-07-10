import {Format} from "../../Format.js";

export class ovationPro extends Format
{
	name           = "Ovation Pro Document";
	ext            = [".dpd"];
	forbidExtMatch = true;
	magic          = ["Ovation Pro"];
	converters     = ["strings"];
}
