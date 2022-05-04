import {Format} from "../../Format.js";

export class coreAudio extends Format
{
	name         = "CoreAudio Format";
	website      = "http://fileformats.archiveteam.org/wiki/Core_Audio_Format";
	ext          = [".caf"];
	magic        = ["CoreAudio Format", "Core Audio File", /^fmt\/416( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
