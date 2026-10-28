import {Format} from "../../Format.js";

export class magicOfEndoriaSoundSample extends Format
{
	name           = "Magic of Endoria Sound Sample";
	ext            = [".snd", ".smp"];
	forbidExtMatch = true;
	magic          = ["Magic of Endoria Sound Sample"];
	converters     = ["vibe2wav[renameOut]"];
}
