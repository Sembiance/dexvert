import {Format} from "../../Format.js";

export class mp3 extends Format
{
	name           = "MPG Layer 3 Audio File";
	website        = "http://fileformats.archiveteam.org/wiki/MP3";
	ext            = [".mp3", ".mpga", ".mpg"];
	forbidExtMatch = [".mpg"];
	mimeType       = "audio/mpeg";
	magic          = ["LAME encoded MP3 audio", /^Audio file.* layer III/, "MPEG ADTS, layer III", "MPEG 1/2 Audio Layer 3", "Audio file with ID3 version 2.3.0", /^MP3 ID3 tag, v2\.\d$/];
	weakMagic      = ["LAME encoded MP3 audio", "MPEG ADTS, layer III"];
	untouched      = true;
	metaProvider   = ["soxi"];
}
