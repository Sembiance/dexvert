import {Format} from "../../Format.js";

export class zincData extends Format
{
	name           = "Zinc Data";
	website        = "https://en.wikipedia.org/wiki/Zinc_Application_Framework";
	ext            = [".dat", ".znc", ".z_t"];
	forbidExtMatch = true;
	magic          = ["Zinc Data"];
	converters     = ["strings"];
}
