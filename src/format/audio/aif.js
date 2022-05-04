import {Format} from "../../Format.js";

export class aif extends Format
{
	name         = "Audio Interchange File Format";
	website      = "http://fileformats.archiveteam.org/wiki/AIFF";
	ext          = [".aif", ".aiff", ".aff"];
	magic        = ["AIFF Audio Interchange File Format", "IFF data, AIFF audio", "Audio Interchange File Format", /^fmt\/414( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]", "vgmstream"];
}
