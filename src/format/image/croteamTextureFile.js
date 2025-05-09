import {Format} from "../../Format.js";

export class croteamTextureFile extends Format
{
	name           = "Croteam texture file";
	ext            = [".tex", ".tbn"];
	forbidExtMatch = true;
	magic          = ["Croteam texture file"];
	converters     = ["wuimg"];
}
