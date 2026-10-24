import {Format} from "../../Format.js";

export class valveXWV extends Format
{
	name           = "Valve XWV Audio";
	ext            = [".wav", ".lwav"];
	forbidExtMatch = true;
	magic          = ["Valve XWV (xwv)", "vgmstream: xwv_valve"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[format:xwv][libre][outType:mp3]", "vgmstream[types:xwv_valve]"];
}
