import {Format} from "../../Format.js";

export class sonyXVAG extends Format
{
	name       = "Sony PS3 XVAG";
	ext        = [".xvag"];
	magic      = ["Sony PS3 XVAG (xvag)"];
	converters = ["ffmpeg[format:xvag][outType:mp3]"];
}
