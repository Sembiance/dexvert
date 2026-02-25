import {Format} from "../../Format.js";

export class abyssEngineImageFormat extends Format
{
	name           = "Abyss Engine Image format";
	ext            = [".aei"];
	forbidExtMatch = true;
	magic          = ["Abyss Engine Image format"];
	converters     = ["wuimg[format:aei]"];
}
