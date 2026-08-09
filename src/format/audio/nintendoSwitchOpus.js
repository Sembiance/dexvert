import {Format} from "../../Format.js";

export class nintendoSwitchOpus extends Format
{
	name           = "Nintendo Switch Opus Audio";
	ext            = [".opusnsw"];
	forbidExtMatch = true;
	magic          = ["Nintendo Switch Opus (opns)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:opns][outType:mp3]"];
}
