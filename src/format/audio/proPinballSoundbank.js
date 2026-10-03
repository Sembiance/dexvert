import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class proPinballSoundbank extends Format
{
	name         = "Pro Pinball Soundbank";
	ext          = [".22c", ".11c", ".5c"];
	magic        = ["Pro Pinball Series Soundbank (pp_bnk)"];
	metaProvider = ["ffprobe"];
	converters   = dexState => ([_FFMPEG_CONVERTERS_BUILDER({dexState, format : "pp_bnk", outType : "mp3"})]);
}
