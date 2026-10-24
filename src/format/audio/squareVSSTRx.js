import {Format} from "../../Format.js";

export class squareVSSTRx extends Format
{
	name           = "Square VS STRx Audio";
	ext            = [".vs"];
	forbidExtMatch = true;
	magic          = ["Square VS STRx (vsstr)", "vgmstream: vs_str"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:vsstr][outType:mp3]", "vgmstream[types:vs_str]"];
}
