import {Format} from "../../Format.js";

export class wingzScript extends Format
{
	name           = "Wingz Script";
	ext            = [".scz"];
	forbidExtMatch = true;
	magic          = ["Wingz script", "Wingz compiled script"];
	converters     = ["strings"];
}
