import {Format} from "../../Format.js";

export class au extends Format
{
	name         = "Sun Microsystems Audio File";
	website      = "http://fileformats.archiveteam.org/wiki/AU";
	ext          = [".au", ".snd"];
	magic        = ["NeXT/Sun sound", "Sun/NeXT audio data", "NeXT/Sun uLaw/AUdio format", /^x-fmt\/139( |$)/];
	mimeType     = "audio/basic";
	metaProvider = ["soxi"];
	converters   = ["ffmpeg[outType:mp3]", "sox"];
}
