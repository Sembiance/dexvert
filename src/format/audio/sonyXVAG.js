import {Format} from "../../Format.js";

export class sonyXVAG extends Format
{
	name       = "Sony PS3 XVAG";
	ext        = [".xvag"];
	magic      = ["Sony PS3 XVAG (xvag)", "Sony PlayStation 3 XVAG audio"];
	converters = ["ffmpeg[format:xvag][outType:mp3]"];
}
