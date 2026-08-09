import {Format} from "../../Format.js";

export class nintendoCWV extends Format
{
	name           = "Nintendo CWV Audio";
	ext            = [".cwv"];
	forbidExtMatch = true;
	magic          = ["Nintendo CWV (cwv)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:cwv][outType:mp3]"];
}
