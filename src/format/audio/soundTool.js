import {Format} from "../../Format.js";

export class soundTool extends Format
{
	name           = "SoundTool";
	ext            = [".snd"];
	forbidExtMatch = [".snd"];
	magic          = ["SoundTool audio", /^soxi: sndt$/];
	weakMagic      = true;
	metaProvider   = ["soxi"];
	converters     = ["sox[type:sndt]"];
}
