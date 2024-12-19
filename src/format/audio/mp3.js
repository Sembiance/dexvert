import {Format} from "../../Format.js";
import {_SHOCKWAVE_AUDIO_MAGIC} from "./shockWaveAudio.js";

export class mp3 extends Format
{
	name           = "MPG Layer 3 Audio File";
	website        = "http://fileformats.archiveteam.org/wiki/MP3";
	ext            = [".mp3", ".mpga", ".mpg"];
	safeExt        = ".mp3";	// needed for soxi to work
	forbidExtMatch = [".mpg"];
	mimeType       = "audio/mpeg";
	magic          = [
		// general MP3 magic
		"LAME encoded MP3 audio", /^Audio file.* layer III/, "MPEG ADTS, layer III", "MPEG 1/2 Audio Layer 3", "Audio file with ID3 version", /^ID3v2.\d.0 Tag/, /^MP3 ID3 tag, v2\.\d$/, "audio/mpeg", "MP2/3 (MPEG audio layer 2/3) (mp3)", /^fmt\/134( |$)/,
		
		// specific app-generate MP3 magic
		"GoGo encoded MP3 audio", "Plugger encoded MP3 audio", "Xing encoded MP3 audio", "MP3 Xing Encoder"
	];
	idMeta         = ({macFileType, macFileCreator}) => ["Mp3 ", "MP3 ", "MPG3"].includes(macFileType) || (macFileType==="MPEG" && macFileCreator==="MAmp");
	//weakMagic      = ["LAME encoded MP3 audio", "MPEG ADTS, layer III", "MP2/3 (MPEG audio layer 2/3) (mp3)", /^fmt\/134( |$)/];
	forbiddenMagic = _SHOCKWAVE_AUDIO_MAGIC;	// I believe Shockwave Audio is actually just MP3 underneath but with some extra metadata, still it's format handles converting it and this ensure we properly identify as that
	untouched      = dexState => dexState.meta?.duration>0 && dexState.meta?.sampleRate>0 && dexState.meta.channels>=1;
	metaProvider   = ["soxi"];
}
