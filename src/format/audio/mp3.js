import {Format} from "../../Format.js";

export class mp3 extends Format
{
	name           = "MPG Layer 3 Audio File";
	website        = "http://fileformats.archiveteam.org/wiki/MP3";
	ext            = [".mp3", ".mpga", ".mpg"];
	forbidExtMatch = [".mpg"];
	mimeType       = "audio/mpeg";
	magic          = [
		// general MP3 magic
		"LAME encoded MP3 audio", /^Audio file.* layer III/, "MPEG ADTS, layer III", "MPEG 1/2 Audio Layer 3", "Audio file with ID3 version", /^ID3v2.\d.0 Tag/, /^MP3 ID3 tag, v2\.\d$/, "audio/mpeg",
		
		// specific app-generate MP3 magic
		"GoGo encoded MP3 audio", "Plugger encoded MP3 audio", "Xing encoded MP3 audio", "MP3 Xing Encoder"
	];
	weakMagic      = ["LAME encoded MP3 audio", "MPEG ADTS, layer III"];
	untouched      = true;
	metaProvider   = ["soxi"];
}
