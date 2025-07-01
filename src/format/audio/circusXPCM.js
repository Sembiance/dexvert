import {Format} from "../../Format.js";

export class circusXPCM extends Format
{
	name           = "Circus XPCM Audio";
	ext            = [".pcm"];
	forbidExtMatch = true;
	magic          = ["Circus XPCM (xpcm)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][outType:mp3]"];
}
