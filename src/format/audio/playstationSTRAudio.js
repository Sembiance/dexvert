import {Format} from "../../Format.js";

export class playstationSTRAudio extends Format
{
	name           = "Playstation STR Audio";
	ext            = [".str"];
	forbidExtMatch = true;
	magic          = ["Sony Playstation STR (psxstr)"];
	converters     = ["ffmpeg[libre][format:psxstr][outType:mp3]"];
}
