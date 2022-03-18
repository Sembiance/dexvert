import {Format} from "../../Format.js";
import {_MOV_MAGIC, _MOV_EXT} from "../video/mov.js";

export class quickTimeAudio extends Format
{
	name             = "Apple QuickTime Audio";
	ext              = _MOV_EXT;
	magic            = _MOV_MAGIC;
	confidenceAdjust = () => -10;	// Reduce by 10 so that mov matches first
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]", "qt_flatt"];
}
