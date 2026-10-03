import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class ubisoftSBxBNM extends Format
{
	name         = "Ubisoft SBx BNM Audio";
	ext          = [".bnm"];
	byteCheck    = [{offset : 0, match : [0x00, 0x00, 0x00, 0x00]}];
	metaProvider = ["ffprobe[libre]"];
	converters   = dexState => ([_FFMPEG_CONVERTERS_BUILDER({dexState, format : "ubibnm", outType : "mp3", libre : true})]);
}
