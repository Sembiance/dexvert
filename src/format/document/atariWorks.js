import {Format} from "../../Format.js";

export class atariWorks extends Format
{
	name           = "Atari Works Document";
	ext            = [".stw"];
	forbidExtMatch = true;
	magic          = ["Atari Works Wordprocessor document"];
	converters     = ["strings"];
}
