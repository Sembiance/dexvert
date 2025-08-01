import {Format} from "../../Format.js";

export class aif extends Format
{
	name         = "Audio Interchange File Format";
	website      = "http://fileformats.archiveteam.org/wiki/AIFF";
	ext          = [".aif", ".aiff", ".aff"];
	magic        = [
		// generic
		"AIFF Audio Interchange File Format", "IFF data, AIFF audio", "Audio Interchange File Format", "IFF data, AIFF-C compressed audio", "AIFF audio data", "AIFF-C", "audio/x-aiff", "audio/x-aifc", "Audio IFF (aiff)", /^soxi: aifc?f?$/,
		/^fmt\/414( |$)/, /^x-fmt\/136( |$)/,

		// specific
		"ReCycled Audio Loop Export", "Asobo Studio Games AIF (aif)"
	];
	idMeta       = ({macFileType}) => ["AIFC", "AIFF"].includes(macFileType);
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]", "vgmstream", "awaveStudio[matchType:magic]"];
}
