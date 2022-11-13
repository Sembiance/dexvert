import {Format} from "../../Format.js";

export class sonarc extends Format
{
	name           = "Sonarc Compressed WAV";
	website        = "http://fileformats.archiveteam.org/wiki/Sonarc";
	ext            = [".wv", ".vc", ".snc"];
	forbidExtMatch = true;
	magic          = ["Sonarc compressed WAV audio", /^RIFF.+ WAVE.+ SONARC/];
	converters     = ["sonarcx"];
}
