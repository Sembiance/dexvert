import {Format} from "../../Format.js";

export class konamiGbTs extends Format
{
	name           = "Konami/KCE GbTs Audio";
	ext            = [".gbts"];
	forbidExtMatch = true;
	magic          = ["Konami/KCE GbTs (gbts)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:gbts][outType:mp3]"];
}
