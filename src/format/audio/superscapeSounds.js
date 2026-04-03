import {xu} from "xu";
import {Format} from "../../Format.js";

export class superscapeSounds extends Format
{
	name           = "Superscape Sounds";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = [/^Superscape Sounds/];
	converters     = ["vibe2wav"];
}
