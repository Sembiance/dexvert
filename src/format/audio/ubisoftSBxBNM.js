import {Format} from "../../Format.js";

export class ubisoftSBxBNM extends Format
{
	name         = "Ubisoft SBx BNM Audio";
	ext          = [".bnm"];
	byteCheck    = [{offset : 0, match : [0x00, 0x00, 0x00, 0x00]}];
	metaProvider = ["ffprobe[libre]"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:ubibnm][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
