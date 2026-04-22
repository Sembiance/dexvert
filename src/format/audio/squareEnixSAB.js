import {Format} from "../../Format.js";

export class squareEnixSAB extends Format
{
	name           = "Square Enix SAB";
	ext            = [".sab"];
	forbidExtMatch = true;
	magic          = ["Square Enix SAB (sab)"];
	converters     = ["ffmpeg[format:sab][libre][outType:mp3]"];
}
