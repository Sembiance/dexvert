import {Format} from "../../Format.js";

export class traXTrack extends Format
{
	name           = "TraX Music Track";
	ext            = [".mts"];
	forbidExtMatch = true;
	magic          = ["TraX Music Track"];
	converters     = ["vibe2mid"];
}
