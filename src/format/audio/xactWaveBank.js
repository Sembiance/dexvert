import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class xactWaveBank extends Format
{
	name         = "XACT Wave Bank";
	ext          = [".xwb"];
	magic        = ["XACT Wave Bank", "Format: Microsoft XACT Wave Bank", "XWB (Microsoft Wave Bank) (xwb)", /^geArchive: (XWB_WBND|XWB_WBND_4|XWB_WBND_3|XWB_WBND_2)( |$)/];
	metaProvider = ["ffprobe[libre]"];
	converters   = dexState => [_FFMPEG_CONVERTERS_BUILDER({dexState, format : "xwb", outType : "mp3", libre : true}), "zxtune123"];
}
