import {Format} from "../../Format.js";

export class knowledgeAdventureSound extends Format
{
	name           = "Knowledge Adventure Sound";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Knowledge Adventure Sound"];
	converters     = ["awaveStudio"];
}
