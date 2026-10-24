import {Format} from "../../Format.js";

export class yukesYMF extends Format
{
	name           = "Yuke's YMF Audio";
	ext            = [".wmw"];
	forbidExtMatch = true;
	magic          = ["Yuke's YMF (ymf)", "vgmstream: ymf"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ymf][outType:mp3]", "vgmstream[types:ymf]"];
}
