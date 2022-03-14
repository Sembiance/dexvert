import {Format} from "../../Format.js";

export class palmThoughtManager extends Format
{
	name           = "Palm ThoughtManager";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["Palm ThoughtManager"];
	converters     = ["strings"];
}
