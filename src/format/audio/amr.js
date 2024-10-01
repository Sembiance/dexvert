import {Format} from "../../Format.js";

export class amr extends Format
{
	name         = "Adaptive Multi-Rate";
	website      = "http://fileformats.archiveteam.org/wiki/Adaptive_Multi-Rate_Audio";
	ext          = [".amr", ".3ga"];
	magic        = ["Adaptive Multi-Rate Codec", "AMR (Adaptive Multi Rate) encoded audio", "Adaptive Multi-Rate Wideband ACELP codec", "audio/AMR", "audio/AMR-WB", "3GPP AMR (amr)", /^fmt\/(356|954)( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
