import {Format} from "../../Format.js";

export class mp3 extends Format
{
	name           = "MPG Layer 3 Audio File";
	website        = "http://fileformats.archiveteam.org/wiki/MP3";
	ext            = [".mp3", ".mpga", ".mpg"];
	forbidExtMatch = [".mpg"];
	mimeType       = "audio/mpeg";
	priority       = this.PRIORITY.LOW;
	magic          = [
		// general MP3 magic
		"LAME encoded MP3 audio", /^Audio file.* layer III/, "MPEG ADTS, layer III", "MPEG 1/2 Audio Layer 3", "Audio file with ID3 version", /^ID3v2.\d.0 Tag/, /^MP3 ID3 tag, v2\.\d$/, "audio/mpeg", "MP2/3 (MPEG audio layer 2/3) (mp3)",
		
		// specific app-generate MP3 magic
		"GoGo encoded MP3 audio", "Plugger encoded MP3 audio", "Xing encoded MP3 audio", "MP3 Xing Encoder"
	];
	idMeta       = ({macFileType, macFileCreator}) => (macFileType==="Mp3 " && macFileCreator==="TVOD") || (macFileType==="MPEG" && macFileCreator==="MAmp") || (macFileType==="MPG3" && macFileCreator==="hook");
	weakMagic    = ["LAME encoded MP3 audio", "MPEG ADTS, layer III", "MP2/3 (MPEG audio layer 2/3) (mp3)"];
	untouched    = true;
	metaProvider = ["soxi"];
}
