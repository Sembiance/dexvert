import {Format} from "../../Format.js";

export class binkAudio extends Format
{
	name       = "Bink Audio";
	website    = "https://wiki.multimedia.cx/index.php/Bink_Audio";
	ext        = [".binka"];
	magic      = ["Unreal Engine Bink Audio (ueba)"];
	converters = ["ffmpeg[libre][format:ueba][outType:mp3]"];
}
