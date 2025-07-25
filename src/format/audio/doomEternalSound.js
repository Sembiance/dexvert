import {Format} from "../../Format.js";

export class doomEternalSound extends Format
{
	name           = "Doom Eternal Sound";
	ext            = [".sfx", ".snd"];
	forbidExtMatch = true;
	magic          = ["Doom Eternal Sound"];
	converters     = ["foremost -> sox"];
}
