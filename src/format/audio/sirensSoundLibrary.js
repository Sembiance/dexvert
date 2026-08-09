import {Format} from "../../Format.js";

export class sirensSoundLibrary extends Format
{
	name           = "Sirens Sound Library Audio";
	ext            = [".ms"];
	forbidExtMatch = true;
	magic          = ["Sirens Sound Library SL3 (sl3)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:sl3][outType:mp3]"];
}
