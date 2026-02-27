import {Format} from "../../Format.js";

export class fableLostChaptersBIGB extends Format
{
	name           = "Fable: The Lost Chaptes BIGB Archive";
	ext            = [".big"];
	forbidExtMatch = true;
	magic          = ["dragon: BIGB "];
	converters     = ["dragonUnpacker[types:BIGB]"];
}
