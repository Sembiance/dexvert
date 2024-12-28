import {Format} from "../../Format.js";

export class soundTool extends Format
{
	name           = "SoundTool";
	ext            = [".snd"];
	forbidExtMatch = [".snd"];
	magic          = ["SoundTool audio"];
	weakMagic      = true;
	metaProvider   = ["soxi"];
	converters     = ["sox"];
}
