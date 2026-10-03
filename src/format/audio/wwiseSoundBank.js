import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class wwiseSoundBank extends Format
{
	name           = "Wwise sound Bank";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["Wwise sound Bank", /^Wwise SoundBank/, "Wwise soundbank container BKHD (bkhd)", /^geArchive: BNK_BKHD( |$)/];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([
		_FFMPEG_CONVERTERS_BUILDER({dexState, format : "bkhd", outType : "mp3", libre : true}),
		"gameextractor[codes:BNK_BKHD] -> dexvert[asFormat:audio/audiokineticWWISE]"
	]);
}
