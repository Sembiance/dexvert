import {Format} from "../../Format.js";

export class ubisoftRayman2APM extends Format
{
	name           = "Ubisoft Rayman 2 APM";
	ext            = [".apm"];
	forbidExtMatch = true;
	magic          = ["Ubisoft Rayman 2 APM (apm)", "Ubisoft APM (apm)"];
	converters     = ["ffmpeg[format:apm][libre][outType:mp3]", "ffmpeg[format:apm][outType:mp3]"];
}
