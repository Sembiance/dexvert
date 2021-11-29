import {Format} from "../../Format.js";

export class developerStudioProject extends Format
{
	name           = "Microsoft Developer Studio Project";
	ext            = [".mdp"];
	forbidExtMatch = true;
	magic          = ["Microsoft Developer Studio Project"];
	converters     = ["strings"];
}
