import {Format} from "../../Format.js";

export class cyberflixDreamFactoryCFDFAudio extends Format
{
	name           = "Cyberflix DreamFactory CFDF Audio";
	ext            = [".trk"];
	forbidExtMatch = true;
	magic          = ["CFDF (Cyberflix DreamFactory) (cfdf)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:cfdf][outType:mp3]"];
	verify         = ({soxiMeta}) => soxiMeta.duration>100;
}
