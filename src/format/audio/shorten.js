import {Format} from "../../Format.js";

export class shorten extends Format
{
	name         = "Shorten Losless Audio";
	website      = "https://wiki.multimedia.cx/index.php?title=Shorten";
	ext          = [".shn"];
	magic        = ["Shorten lossless compressed audio"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]"];
}
