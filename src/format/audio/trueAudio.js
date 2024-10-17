import {Format} from "../../Format.js";

export class trueAudio extends Format
{
	name       = "TrueAudio Lossless Audio";
	website    = "https://wiki.hydrogenaud.io/index.php?title=TTA";
	ext        = [".tta"];
	magic      = ["True Audio Lossless Audio", "audio/x-tta", "TTA True Audio lossless compressed audio", "TTA (True Audio) (tta)", /^fmt\/952( |$)/];
	weakMagic  = ["TTA True Audio lossless compressed audio"];
	converters = ["ffmpeg[format:tta][outType:mp3]", "ttaenc"];
}
