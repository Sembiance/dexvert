import {Format} from "../../Format.js";

export class proPinballSoundbank extends Format
{
	name         = "Pro Pinball Soundbank";
	ext          = [".22c", ".11c", ".5c"];
	magic        = ["Pro Pinball Series Soundbank (pp_bnk)"];
	metaProvider = ["ffprobe"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[format:pp_bnk][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
