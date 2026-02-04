import {Format} from "../../Format.js";

export class cyberflixDreamFactoryCFDFAudio extends Format
{
	name           = "Cyberflix DreamFactory CFDF Audio";
	ext            = [".trk"];
	forbidExtMatch = true;
	magic          = ["CFDF (Cyberflix DreamFactory) (cfdf)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:cfdf][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
	verify         = ({soxiMeta}) => soxiMeta.duration>10;
}
