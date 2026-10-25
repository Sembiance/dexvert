import {Format} from "../../Format.js";

export class playDateVideo extends Format
{
	name           = "PlayDate Video";
	ext            = [".pdv"];
	forbidExtMatch = true;
	magic          = ["PlayDate Video (pdv)"];
	metaProvider   = ["ffprobe"];
	converters     = ["ffmpeg[format:pdv]", "ffmpeg[libre][format:pdv]"];
}
