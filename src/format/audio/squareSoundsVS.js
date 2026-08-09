import {Format} from "../../Format.js";

export class squareSoundsVS extends Format
{
	name           = "Square Sounds VS Audio";
	ext            = [".vs"];
	forbidExtMatch = true;
	magic          = ["Square Sounds VS (vs00)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:vs00][outType:mp3]"];
}
