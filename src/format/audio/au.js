import {Format} from "../../Format.js";

export class au extends Format
{
	name         = "Sun Microsystems Audio File";
	website      = "http://fileformats.archiveteam.org/wiki/AU";
	ext          = [".au", ".snd"];
	magic        = ["NeXT/Sun sound", "Sun/NeXT audio data", "NeXT/Sun uLaw/AUdio format"];
	mimeType     = "audio/basic";
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
