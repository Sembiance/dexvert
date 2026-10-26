import {Format} from "../../Format.js";

export class fujitsuMovie extends Format
{
	name           = "Fujitsu Movie";
	ext            = [".mve"];
	forbidExtMatch = true;
	magic          = ["Fujitsu Movie format video", "Generic RIFF file FJMV"];
	converters     = ["vibe2avi"];
}
