import {Format} from "../../Format.js";

export class unrealEngine4Opus extends Format
{
	name           = "Unreal Engine 4 Opus Audio";
	ext            = [".ue4opus"];
	forbidExtMatch = true;
	magic          = ["Unreal Engine 4 Opus (ue4opus)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ue4opus][outType:mp3]"];
}
