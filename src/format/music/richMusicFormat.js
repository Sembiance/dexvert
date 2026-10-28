import {Format} from "../../Format.js";

export class richMusicFormat extends Format
{
	name           = "Rich Music Format";
	ext            = [".rmf"];
	forbidExtMatch = true;
	magic          = ["Rich Music Format"];
	converters     = ["vibe2wav"];
}
