import {Format} from "../../Format.js";

export class dageshDocument extends Format
{
	name           = "Dagesh Document";
	ext            = [".dgs"];
	forbidExtMatch = true;
	magic          = ["Dagesh document"];
	converters     = ["strings"];
}
