import {Format} from "../../Format.js";

export class mattelAUDV extends Format
{
	name           = "Mattel AUDV Audio";
	ext            = [".audv"];
	forbidExtMatch = true;
	magic          = ["Mattel AUDV (audv)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:audv][outType:mp3]"];
}
