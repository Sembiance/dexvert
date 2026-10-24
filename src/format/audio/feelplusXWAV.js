import {Format} from "../../Format.js";

export class feelplusXWAV extends Format
{
	name           = "feelplus XWAV Audio";
	ext            = [".xwv"];
	forbidExtMatch = true;
	magic          = ["feelplus XWAV (xwav)", "vgmstream: xwav_old"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:xwav][outType:mp3]", "vgmstream[types:xwav_old]"];
}
