import {Format} from "../../Format.js";

export class acornReplayAudio extends Format
{
	name             = "Acorn Replay Audio";
	website          = "http://fileformats.archiveteam.org/wiki/Acorn_Replay";
	ext              = [".rpl"];
	magic            = ["ARMovie", "RPL / ARMovie (rpl)"];
	confidenceAdjust = () => -10;	// Reduce by 10 so that acornReplayVideo matches first
	metaProvider     = ["mplayer"];
	converters       = ["nihav[outType:mp3]", "ffmpeg[format:rpl]"];
}
