
import {Format} from "../../Format.js";

export class steveSND extends Format
{
	name           = "STEVE SND";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Steve sound format"];
	converters     = ["steve2wav"];
}
