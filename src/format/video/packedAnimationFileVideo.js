import {Format} from "../../Format.js";

export class packedAnimationFileVideo extends Format
{
	name         = "Packed Animation File Video";
	ext          = [".paf"];
	magic        = ["Packed Animation File video"];
	notes        = "Only 1 sample file has been located and ffmpeg (the only converter I could find) fails to process it. Submitted an ffmpeg bug: https://trac.ffmpeg.org/ticket/9362";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:paf]"];
}
