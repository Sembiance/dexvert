import {Format} from "../../Format.js";

export class wav extends Format
{
	name         = "Waveform Audio File Format";
	website      = "http://fileformats.archiveteam.org/wiki/WAV";
	ext          = [".wav"];
	mimeType     = "audio/x-wav";
	magic        = ["RIFF/WAVe standard Audio", /^RIFF.* WAVE audio/, "Waveform Audio (PCMWAVEFORMAT)"];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[format:wav][outType:mp3]"];
}
