import {Format} from "../../Format.js";

export class nexEntertainmentNXAP extends Format
{
	name           = "Nex Entertainment NXAP Audio";
	ext            = [".adp"];
	forbidExtMatch = true;
	magic          = ["Nex Entertainment NXAP (nxap)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:nxap][outType:mp3]"];
}
