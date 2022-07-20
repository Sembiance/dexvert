import {Format} from "../../Format.js";

export class cubicPlayerModuleInfoDB extends Format
{
	name           = "Cubic Player Module Information Database";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Cubic Player module information data base"];
	converters     = ["strings"];
}
