import {Format} from "../../Format.js";

export class wwiseSoundBank extends Format
{
	name           = "Wwise sound Bank";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["Wwise sound Bank", /^Wwise SoundBank/, "Wwise soundbank container BKHD (bkhd)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:bkhd][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
