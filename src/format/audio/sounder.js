import {Format} from "../../Format.js";

export class sounder extends Format
{
	name           = "Sounder";
	ext            = [".snd"];
	forbidExtMatch = [".snd"];
	magic          = [/^soxi: sndr$/];
	weakMagic      = true;
	metaProvider   = ["soxi"];
	converters     = ["sox"];
}
