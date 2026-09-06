import {Format} from "../../Format.js";

export class sirtechNSRSAudio extends Format
{
	name       = "Sirtech NSRS Audio";
	ext        = [".16", ".8"];
	forbidExtMatch = true;
	magic      = ["Sirtech NSRS Audio"];
	converters = ["na_game_tool[format:nsrs][outType:wav]"];
}
