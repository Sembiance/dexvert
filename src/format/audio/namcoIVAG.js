import {Format} from "../../Format.js";

export class namcoIVAG extends Format
{
	name           = "Namco IVAG Audio";
	ext            = [".ivag"];
	forbidExtMatch = true;
	magic          = ["Namco IVAG (ivag)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:ivag][outType:mp3]"];
}
