import {Format} from "../../Format.js";

export class threeDOSTRAudio extends Format
{
	name       = "3DO STR audio";
	magic      = ["3DO STR (3dostr)"];
	converters = ["ffmpeg[format:3dostr][outType:mp3]"];	// ffmpeg only seems to support audio, not video
}
