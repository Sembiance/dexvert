import {Format} from "../../Format.js";

export class palmTealMeal extends Format
{
	name           = "Palm TealMeal Document";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["Palm TealMeal"];
	converters     = ["strings"];
}
