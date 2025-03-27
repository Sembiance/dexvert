import {Format} from "../../Format.js";

export class highCompressionAudio extends Format
{
	name           = "High Compression Audio";
	ext            = [".hca"];
	forbidExtMatch = true;
	magic          = ["High Compression Audio", "CRI HCA (hca)"];
	converters     = ["ffmpeg[format:hca][outType:mp3]"];
}
