import {Format} from "../../Format.js";

export class wav extends Format
{
	name         = "Waveform Audio File Format";
	website      = "http://fileformats.archiveteam.org/wiki/WAV";
	ext          = [".wav", ".bwf"];
	mimeType     = "audio/x-wav";
	magic        = [
		/^RIFF.*WAV[Ee].*[aA]udio/, "Waveform Audio (PCMWAVEFORMAT)", "Wave Musikdatei (WAV)", "Broadcast Wave File audio", "RIFF audio data (WAV)", "Rockwell ADPCM audio", "audio/vnd.wave", "WAV / WAVE (Waveform Audio) (wav)",
		/^fmt\/(2|6|141|142|143|703|704)( |$)/
	];
	idMeta       = ({macFileType}) => [".WAV", "WAVE"].includes(macFileType);
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[format:wav][outType:mp3]", "awaveStudio"];
}
