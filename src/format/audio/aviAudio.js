import {Format} from "../../Format.js";
import {_AVI_MAGIC} from "../video/avi.js";

export class aviAudio extends Format
{
	name             = "AVI Audio";
	ext              = [".avi"];
	magic            = _AVI_MAGIC;
	confidenceAdjust = () => -10;	// Reduce by 10 so that avi matches first
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]", "awaveStudio"];
}
