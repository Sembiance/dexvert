import {Format} from "../../Format.js";

export class monkeysAudio extends Format
{
	name         = "Monkey's Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Monkey's_Audio";
	ext          = [".ape"];
	magic        = ["Monkey's Audio", "Monkeys Audio music file", /^fmt\/1086( |$)/];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]", "zxtune123"];
}
