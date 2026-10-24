import {Format} from "../../Format.js";

export class alphaOgg extends Format
{
	name           = "Alpha Ogg Audio";
	ext            = [".ao"];
	forbidExtMatch = true;
	magic          = ["AlphaOgg (ao)", "Alpha Ogg Audio", "vgmstream: alphaogg"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[outType:mp3][libre]", "vgmstream[types:alphaogg]"];
}
