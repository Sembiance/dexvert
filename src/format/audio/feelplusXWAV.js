import {Format} from "../../Format.js";

export class feelplusXWAV extends Format
{
	name           = "feelplus XWAV Audio";
	ext            = [".xwv"];
	forbidExtMatch = true;
	magic          = ["feelplus XWAV (xwav)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:xwav][outType:mp3]"];
}
