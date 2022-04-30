import {Format} from "../../Format.js";

export class amr extends Format
{
	name         = "Adaptive Multi-Rate";
	website      = "http://fileformats.archiveteam.org/wiki/Adaptive_Multi-Rate_Audio";
	ext          = [".amr", ".3ga"];
	magic        = ["Adaptive Multi-Rate Codec", "AMR (Adaptive Multi Rate) encoded audio"];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
