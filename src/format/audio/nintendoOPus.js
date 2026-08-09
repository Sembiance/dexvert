import {Format} from "../../Format.js";

export class nintendoOPus extends Format
{
	name           = "Nintendo OPus Audio";
	ext            = [".opusnsw"];
	forbidExtMatch = true;
	magic          = ["Nintendo OPus (nop)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:nop][outType:mp3]"];
}
