import {Format} from "../../Format.js";

export class mlpAudio extends Format
{
	name         = "Dolby Lossless Predictive Audio";
	website      = "https://wiki.multimedia.cx/index.php/Lossless_Predictive_Audio_Coding";
	ext          = [".mlp"];
	magic        = ["Meridian Lossless Packing audio", "raw MLP (mlp)", /^fmt\/972( |$)/];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:mlp][outType:mp3]"];
}
