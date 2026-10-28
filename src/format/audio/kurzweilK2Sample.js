import {Format} from "../../Format.js";

export class kurzweilK2Sample extends Format
{
	name           = "Kurzweil K2 Sample";
	ext            = [".kr1", ".kr2", ".krz"];
	forbidExtMatch = true;
	magic          = ["Kurzweil K2-serie sample"];
	converters     = ["vibe2wav"];
}
