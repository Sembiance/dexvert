import {Format} from "../../Format.js";

export class unrealEngine5Opus extends Format
{
	name           = "Unreal Engine 5 Opus Audio";
	ext            = [".ueopus"];
	forbidExtMatch = true;
	magic          = ["Unreal Engine 5 Opus (ueopus)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ueopus][outType:mp3]"];
}
