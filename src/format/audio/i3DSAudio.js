import {Format} from "../../Format.js";

export class i3DSAudio extends Format
{
	name           = "i3DS Audio";
	ext            = [".3ds"];
	forbidExtMatch = true;
	magic          = ["i3DS (i3ds)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:i3ds][outType:mp3]"];
}
