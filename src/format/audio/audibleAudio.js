import {Format} from "../../Format.js";

export class audibleAudio extends Format
{
	name         = "Audible Audio";
	website      = "https://wiki.multimedia.cx/index.php/Audible_Audio";
	ext          = [".aa"];
	magic        = ["Audible Audio", "audio/x-pn-audibleaudio", "Audible AA format files (aa)"];
	converters   = ["ffmpeg[format:aa][outType:mp3]"];
}
