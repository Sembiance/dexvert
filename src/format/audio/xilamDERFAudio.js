import {Format} from "../../Format.js";

export class xilamDERFAudio extends Format
{
	name       = "Xilam DERF Audio";
	website    = "https://wiki.multimedia.cx/index.php/Xilam_DERF";
	ext        = [".adp"];
	magic      = ["Xilam DERF audio", "Xilam DERF (derf)"];
	converters = ["ffmpeg[format:derf][outType:mp3]"];
}
