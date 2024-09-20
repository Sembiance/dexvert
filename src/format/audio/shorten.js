import {Format} from "../../Format.js";

export class shorten extends Format
{
	name         = "Shorten Losless Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Shorten";
	ext          = [".shn"];
	magic        = ["Shorten lossless compressed audio", "application/x-shorten"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]"];
}
