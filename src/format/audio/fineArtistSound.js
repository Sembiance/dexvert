import {Format} from "../../Format.js";

export class fineArtistSound extends Format
{
	name           = "Fine Artist Sound";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Fine Artist Sound"];
	converters     = ["vibe2wav"];
}
