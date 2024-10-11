import {Format} from "../../Format.js";

export class simonSchusterVAG extends Format
{
	name           = "Simon & Schuster Interactive VAG";
	ext            = [".vag"];
	forbidExtMatch = true;
	magic          = ["Simon & Schuster Interactive VAG (kvag)"];
	converters     = ["ffmpeg[format:kvag][outType:mp3]"];
}
