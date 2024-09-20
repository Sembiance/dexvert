import {Format} from "../../Format.js";

export class aif extends Format
{
	name         = "Audio Interchange File Format";
	website      = "http://fileformats.archiveteam.org/wiki/AIFF";
	ext          = [".aif", ".aiff", ".aff"];
	magic        = ["AIFF Audio Interchange File Format", "IFF data, AIFF audio", "Audio Interchange File Format", "IFF data, AIFF-C compressed audio", "AIFF audio data", "AIFF-C", "audio/x-aiff", "audio/x-aifc", /^fmt\/414( |$)/, /^x-fmt\/136( |$)/];
	idMeta       = ({macFileType}) => ["AIFC", "AIFF"].includes(macFileType);
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]", "vgmstream", "awaveStudio"];
}
