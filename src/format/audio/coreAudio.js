import {Format} from "../../Format.js";

export class coreAudio extends Format
{
	name         = "CoreAudio Format";
	website      = "http://fileformats.archiveteam.org/wiki/Core_Audio_Format";
	ext          = [".caf"];
	magic        = ["CoreAudio Format", "Core Audio File", "Core Audio Format", "Apple CAF (Core Audio Format) (caf)", /^soxi: caf$/, /^fmt\/416( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox[type:caf]", "ffmpeg[format:caf][outType:mp3]"];
}
