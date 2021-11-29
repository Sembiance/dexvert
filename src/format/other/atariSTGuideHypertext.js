import {Format} from "../../Format.js";

export class atariSTGuideHypertext extends Format
{
	name           = "Atari ST Guide Hypertext";
	ext            = [".hyp"];
	forbidExtMatch = true;
	magic          = ["Atari ST Guide Hypertext document", "Atari ST Guide Hypertext"];
	converters     = ["strings"];
}
