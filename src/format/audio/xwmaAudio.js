import {Format} from "../../Format.js";

export class xwmaAudio extends Format
{
	name           = "Microsoft XWMA Audio";
	ext            = [".xwma", ".xwm"];
	forbidExtMatch = true;
	magic          = ["XWMA audio", "Microsoft xWMA (xwma)", "Generic RIFF file XWMA", /^fmt\/923( |$)/];
	converters     = ["ffmpeg[format:xwma][outType:mp3]"];
}
