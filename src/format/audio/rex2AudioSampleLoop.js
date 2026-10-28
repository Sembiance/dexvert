import {Format} from "../../Format.js";

export class rex2AudioSampleLoop extends Format
{
	name           = "REX2 audio sample loop";
	ext            = [".rx2", ".rex"];
	forbidExtMatch = true;
	magic          = ["REX2 audio sample loop"];
	converters     = ["vibe2wav[renameOut]"];
}
