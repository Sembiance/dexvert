import {Format} from "../../Format.js";

export class novastormMediaAnimation extends Format
{
	name           = "Novastorm Media animation";
	ext            = [".flm"];
	forbidExtMatch = true;
	magic          = ["Novastorm Media animation"];
	converters     = ["vibe2avi"];
}
