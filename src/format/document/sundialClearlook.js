import {Format} from "../../Format.js";

export class sundialClearlook extends Format
{
	name           = "Sundial Clearlook";
	ext            = [".ctx"];
	forbidExtMatch = true;
	magic          = ["Sundial Clearlook document"];
	converters     = ["strings"];
}
