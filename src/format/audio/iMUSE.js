import {Format} from "../../Format.js";

export class iMUSE extends Format
{
	name           = "iMUSE Audio";
	ext            = [".imc", ".imx"];
	forbidExtMatch = true;
	magic          = ["iMUSE (LucasArts Interactive Streaming Engine) (imuse)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:imuse][outType:mp3]"];
}
