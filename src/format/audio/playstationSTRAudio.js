import {Format} from "../../Format.js";

export class playstationSTRAudio extends Format
{
	name           = "Playstation STR Audio";
	ext            = [".str"];
	forbidExtMatch = true;
	magic          = ["Sony Playstation STR (psxstr)"];
	weakMagic      = true;
	converters     = ["ffmpeg[libre][format:psxstr][outType:mp3]"];
}
