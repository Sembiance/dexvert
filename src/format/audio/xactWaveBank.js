import {Format} from "../../Format.js";

export class xactWaveBank extends Format
{
	name         = "XACT Wave Bank";
	ext          = [".xwb"];
	magic        = ["XACT Wave Bank", "Format: Microsoft XACT Wave Bank", "XWB (Microsoft Wave Bank) (xwb)", /^geArchive: (XWB_WBND|XWB_WBND_3)( |$)/];
	metaProvider = ["ffprobe[libre]"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:xwb][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & "), "zxtune123"]);
}
