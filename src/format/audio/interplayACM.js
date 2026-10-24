import {Format} from "../../Format.js";

export class interplayACM extends Format
{
	name           = "Interplay Compressed Audio";
	website        = "http://fileformats.archiveteam.org/wiki/Interplay_ACM";
	ext            = [".acm"];
	forbidExtMatch = true;
	magic          = ["Interplay Compressed Audio Format", "Interplay ACM (acm)", "vgmstream: acm"];
	metaProvider   = ["ffprobe"];
	converters     = ["ffmpeg[format:acm][outType:mp3]", "vgmstream[types:acm]", "acm2wav"];
}
