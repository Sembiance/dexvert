import {Format} from "../../Format.js";

export class namcoMUS extends Format
{
	name           = "Namco MUS Audio";
	ext            = [".ivag"];
	forbidExtMatch = true;
	magic          = ["Namco MUS (mus)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:mus][outType:mp3]"];
}
