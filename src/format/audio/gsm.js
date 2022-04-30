import {Format} from "../../Format.js";

export class gsm extends Format
{
	name         = "GSM Audio";
	website      = "http://fileformats.archiveteam.org/wiki/GSM";
	ext          = [".gsm"];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
