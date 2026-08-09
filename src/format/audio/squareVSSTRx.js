import {Format} from "../../Format.js";

export class squareVSSTRx extends Format
{
	name           = "Square VS STRx Audio";
	ext            = [".vs"];
	forbidExtMatch = true;
	magic          = ["Square VS STRx (vsstr)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:vsstr][outType:mp3]"];
}
