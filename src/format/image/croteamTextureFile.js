import {Format} from "../../Format.js";

export class croteamTextureFile extends Format
{
	name           = "Croteam texture file";
	ext            = [".tex", ".tbn"];
	forbidExtMatch = true;
	magic          = ["Croteam texture file", "Croteam texture Min"];
	converters     = ["wuimg[format:tbn]"];
}
