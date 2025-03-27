import {Format} from "../../Format.js";

export class xboxSDNS extends Format
{
	name           = "Xbox SDNS";
	ext            = [".xma"];
	forbidExtMatch = true;
	magic          = ["Xbox SDNS (sdns)"];
	converters     = ["ffmpeg[format:sdns][outType:mp3]"];
}
