import {Format} from "../../Format.js";

export class databenchData extends Format
{
	name           = "Databench Data";
	forbidExtMatch = true;
	magic          = ["Databench data"];
	converters     = ["strings"];
}
