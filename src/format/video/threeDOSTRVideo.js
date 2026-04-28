import {Format} from "../../Format.js";

export class threeDOSTRVideo extends Format
{
	name         = "3DO STR video";
	magic        = ["3DO STR (3dostr)"];
	metaProvider = ["mplayer"];
	unsupported  = true;	// 0 files on discmaster
	//converters   = ["ffmpeg[format:3dostr]"];	// ffmpeg only seems to support audio, not video
}
