import {Format} from "../../Format.js";

export class rockstarGamesRSTM extends Format
{
	name           = "Rockstar Games RSTM";
	ext            = [".rstm"];
	forbidExtMatch = true;
	magic          = ["RSTM (Rockstar Games) (rstm)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:rstm][outType:mp3]"];
}
