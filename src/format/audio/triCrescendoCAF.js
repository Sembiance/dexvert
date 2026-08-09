import {Format} from "../../Format.js";

export class triCrescendoCAF extends Format
{
	name           = "Tri-Crescendo CAF Audio";
	ext            = [".cfn"];
	forbidExtMatch = true;
	magic          = ["tri-Crescendo CAF (cfn)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:cfn][outType:mp3]"];
}
