import {Format} from "../../Format.js";

export class infinityEngineGraphic extends Format
{
	name           = "Infinity Engine Graphic";
	ext            = [".mos"];
	forbidExtMatch = true;
	magic          = ["Infinity Engine graphic", "Infinity Engine compressed graphic"];
	converters     = ["vibe2png"];
}
