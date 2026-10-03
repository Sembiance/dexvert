import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class cyberflixDreamFactoryCFDFAudio extends Format
{
	name           = "Cyberflix DreamFactory CFDF Audio";
	ext            = [".trk"];
	forbidExtMatch = true;
	magic          = ["CFDF (Cyberflix DreamFactory) (cfdf)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => ([_FFMPEG_CONVERTERS_BUILDER({dexState, format : "cfdf", outType : "mp3", libre : true})]);
	verify         = ({soxiMeta}) => soxiMeta.duration>10;
}
