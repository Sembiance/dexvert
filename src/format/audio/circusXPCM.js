import {Format} from "../../Format.js";

export class circusXPCM extends Format
{
	name           = "Circus XPCM Audio";
	ext            = [".pcm"];
	forbidExtMatch = true;
	magic          = ["Circus XPCM (xpcm)", "audio:Circus.PcmAudio", "vgmstream: xpcm"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][outType:mp3]", "vgmstream[types:xpcm]", "GARbro[types:audio:Circus.PcmAudio]"];
}
