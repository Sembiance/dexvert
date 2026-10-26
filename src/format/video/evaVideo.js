import {Format} from "../../Format.js";

export class evaVideo extends Format
{
	name           = "EVA3/EVA5 video";
	ext            = [".eva"];
	forbidExtMatch = true;
	magic          = [/^EVA[35] video$/];
	converters     = ["vibe2avi"];
}
