import {Format} from "../../Format.js";

export class atariWorksDatabase extends Format
{
	name           = "Atari Works Database";
	ext            = [".std"];
	forbidExtMatch = true;
	magic          = ["Atari Works Database"];
	converters     = ["strings"];
}
