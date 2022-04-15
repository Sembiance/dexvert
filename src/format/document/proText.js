import {Format} from "../../Format.js";

export class proText extends Format
{
	name           = "ProText Document";
	forbidExtMatch = true;
	magic          = ["Protext document"];
	converters     = ["strings"];
}
