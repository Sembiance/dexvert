import {Format} from "../../Format.js";

export class knowledgeAdventureSound extends Format
{
	name           = "Knowledge Adventure Sound";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Knowledge Adventure Sound", "vgmstream: ka"];
	converters     = ["vgmstream[types:ka]", "awaveStudio"];
}
