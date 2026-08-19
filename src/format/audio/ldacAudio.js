import {Format} from "../../Format.js";

export class ldacAudio extends Format
{
	name           = "LDAC Audio";
	ext            = [".ldac"];
	forbidExtMatch = true;
	magic          = ["LDAC (ldac)"];
	weakMagic      = true;
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ldac][outType:mp3]"];
}
