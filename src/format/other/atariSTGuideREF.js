import {Format} from "../../Format.js";

export class atariSTGuideREF extends Format
{
	name           = "Atari ST Guide REF Links";
	ext            = [".ref"];
	forbidExtMatch = true;
	magic          = ["Atari ST Guide ref links"];
	converters     = ["strings"];
}
