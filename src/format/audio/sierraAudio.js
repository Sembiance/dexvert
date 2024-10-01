import {Format} from "../../Format.js";

export class sierraAudio extends Format
{
	name         = "Sierra Audio";
	website      = "https://wiki.multimedia.cx/index.php/Sierra_Audio";
	ext          = [".sfx", ".sol"];
	magic        = [/^Sierra On-Line.* audio$/, "Sierra SOL (sol)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:sol][outType:mp3]"];
}
