import {Format} from "../../Format.js";

export class threeGAudio extends Format
{
	name             = "3GP/3GPP2 Audio";
	website          = "http://fileformats.archiveteam.org/wiki/3GP";
	ext              = [".3gp", ".3g2"];
	magic            = ["3GPP/3GPP2 multimedia audio/video", "ISO Media, MPEG v4 system, 3GPP2", "video/3gpp"];
	confidenceAdjust = () => -9;	// Reduce by 9 so that threeGVideo matches first but this matches before video/mp4 (V0814400.m4a)
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]"];
}
