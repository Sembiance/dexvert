import {Format} from "../../Format.js";

export class unrealEngine5XMA extends Format
{
	name           = "Unreal Engine 5 XMA Audio";
	ext            = [".xma"];
	forbidExtMatch = true;
	magic          = ["Unreal Engine 5 XMA (ue5xma)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ue5xma][outType:mp3]"];
}
