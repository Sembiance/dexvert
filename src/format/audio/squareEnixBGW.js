import {Format} from "../../Format.js";

export class squareEnixBGW extends Format
{
	name           = "Square Enix BGW Audio";
	ext            = [".bgw"];
	forbidExtMatch = true;
	magic          = ["Square Enix BGW (bgw)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:bgw][outType:mp3]"];
}
