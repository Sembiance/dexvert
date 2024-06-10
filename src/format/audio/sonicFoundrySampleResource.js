import {Format} from "../../Format.js";

export class sonicFoundrySampleResource extends Format
{
	name           = "Sonic Foundry Sample Resource";
	ext            = [".sfr"];
	forbidExtMatch = true;
	magic          = ["Sonic Foundry Sample Resource"];
	converters     = ["awaveStudio"];
}
