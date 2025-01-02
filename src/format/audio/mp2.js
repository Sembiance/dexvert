import {Format} from "../../Format.js";

export class mp2 extends Format
{
	name           = "MPEG ADTS Layer II";
	website        = "http://fileformats.archiveteam.org/wiki/MPEG_Audio_Layer_II";
	ext            = [".mp2"];
	forbidExtMatch = true;
	magic          = ["MPEG ADTS, layer II", /^soxi: mp2$/, /^fmt\/198( |$)/];
	metaProvider   = ["soxi"];
	converters     = ["ffmpeg[outType:mp3]"];
}
