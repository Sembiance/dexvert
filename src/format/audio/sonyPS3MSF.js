import {Format} from "../../Format.js";

export class sonyPS3MSF extends Format
{
	name           = "Sony PS3 MSF";
	ext            = [".msf"];
	forbidExtMatch = true;
	magic          = ["Sony PS3 MSF (msf)"];
	converters     = ["ffmpeg[format:msf][outType:mp3]"];
}
