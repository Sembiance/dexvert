import {Format} from "../../Format.js";

export class sensauraGameCODASAB extends Format
{
	name           = "Sensaura GameCODA SAB Audio";
	ext            = [".sab"];
	forbidExtMatch = true;
	magic          = ["Sensaura GameCODA SAB (csx2)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:csx2][outType:mp3]"];
}
