import {Format} from "../../Format.js";

export class criAFS extends Format
{
	name           = "CRI AFS";
	ext            = [".afs"];
	forbidExtMatch = true;
	magic          = ["CRI AFS (afs)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:afs][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
