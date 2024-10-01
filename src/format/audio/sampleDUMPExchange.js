import {Format} from "../../Format.js";

export class sampleDUMPExchange extends Format
{
	name           = "Sample DUMP Exchange Audio";
	ext            = [".sdx"];
	forbidExtMatch = true;
	magic          = ["Sample DUMP Exchange audio", "Sample Dump eXchange (sdx)"];
	converters     = ["ffmpeg[format:sdx][outType:mp3]", "awaveStudio"];
}
