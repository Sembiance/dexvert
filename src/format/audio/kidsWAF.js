import {Format} from "../../Format.js";

export class kidsWAF extends Format
{
	name           = "KID's WAF Audio";
	ext            = [".waf"];
	forbidExtMatch = true;
	magic          = ["KID's WAF (waf)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:waf][outType:mp3]"];
}
