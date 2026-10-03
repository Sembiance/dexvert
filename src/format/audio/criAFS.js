import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class criAFS extends Format
{
	name           = "CRI AFS";
	ext            = [".afs"];
	forbidExtMatch = true;
	magic          = ["CRI AFS (afs)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([_FFMPEG_CONVERTERS_BUILDER({dexState, format : "afs", outType : "mp3", libre : true})]);
}
