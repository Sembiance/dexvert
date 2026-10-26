import {Format} from "../../Format.js";

export class novastormMediaVideo extends Format
{
	name           = "Novastorm Media video";
	ext            = [".fa", ".fza", ".mza"];
	forbidExtMatch = true;
	magic          = ["Novastorm Media video"];
	converters     = ["vibe2avi"];
}
