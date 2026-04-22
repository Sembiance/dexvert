import {Format} from "../../Format.js";

export class alphaOgg extends Format
{
	name           = "Alpha Ogg Audio";
	ext            = [".ao"];
	forbidExtMatch = true;
	magic          = ["AlphaOgg (ao)", "Alpha Ogg Audio"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[outType:mp3][libre]"];
}
