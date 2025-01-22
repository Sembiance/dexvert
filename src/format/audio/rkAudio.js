import {xu} from "xu";
import {Format} from "../../Format.js";

export class rkAudio extends Format
{
	name       = "RK Audio";
	website    = "http://fileformats.archiveteam.org/wiki/RK_Audio";
	ext        = [".rka"];
	magic      = ["RL Audio", "RK Audio lossless compressed audio", "RKA (RK Audio) (rka)"];
	converters = ["ffmpeg[format:rka][outType:mp3]", "rkau"];
}
