import {Format} from "../../Format.js";

export class pivotalPSFBank extends Format
{
	name           = "Pivotal PSF Bank Audio";
	ext            = [".wss", ".psf"];
	forbidExtMatch = true;
	magic          = ["Pivotal PSF Bank (psfb)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:psfb][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
