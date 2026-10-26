import {Format} from "../../Format.js";

export class astoundAnimation extends Format
{
	name           = "Astound Animation";
	ext            = [".awa"];
	forbidExtMatch = true;
	magic          = ["Astound Animation"];
	converters     = ["vibe2avi"];
}
