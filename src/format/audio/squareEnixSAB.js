import {Format} from "../../Format.js";

export class squareEnixSAB extends Format
{
	name           = "Square Enix SAB";
	ext            = [".sab"];
	forbidExtMatch = true;
	magic          = ["Square Enix SAB (sab)", "vgmstream: sqex_sead"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[format:sab][libre][outType:mp3]", "vgmstream[types:sqex_sead]"];
}
