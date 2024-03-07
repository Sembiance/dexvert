import {Format} from "../../Format.js";

export class wav extends Format
{
	name         = "Waveform Audio File Format";
	website      = "http://fileformats.archiveteam.org/wiki/WAV";
	ext          = [".wav"];
	mimeType     = "audio/x-wav";
	magic        = [/^RIFF.*WAV[Ee].*[aA]udio/, "Waveform Audio (PCMWAVEFORMAT)", "Wave Musikdatei (WAV)", /^fmt\/(6|141|142)( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[format:wav][outType:mp3]", "awaveStudio"];
}
