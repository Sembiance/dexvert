import {Format} from "../../Format.js";

export class virtualDJAudioSample extends Format
{
	name           = "VirtualDJ audio Sample";
	ext            = [".vdj"];
	forbidExtMatch = true;
	magic          = ["VirtualDJ audio Sample"];
	converters     = ["ffmpeg[format:mp3][outType:mp3]"];
}
