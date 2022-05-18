import {Format} from "../../Format.js";

export class westwoodStudiosAudio extends Format
{
	name         = "Westwood Studios Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Westwood_Studios_AUD";
	ext          = [".aud"];
	magic        = ["Westwood Studios audio"];
	metaProvider = ["ffprobe"];
	notes        = "Sample file 991.AUD converts to just silence, not sure why.";
	converters   = ["ffmpeg[format:wsaud][outType:mp3]"];
}
