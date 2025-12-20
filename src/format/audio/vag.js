import {Format} from "../../Format.js";

export class vag extends Format
{
	name           = "PlayStation VAG Audio";
	website        = "http://fileformats.archiveteam.org/wiki/VAG_(PlayStation)";
	ext            = [".vag"];
	forbidExtMatch = true;
	magic          = ["PlayStation single waveform data format", "Sony PS2 VAG (vag)", /^soxi: vag$/];
	metaProvider   = ["ffprobe"];
	converters     = ["ffmpeg[format:vag][outType:mp3]", "zxtune123"];
}
