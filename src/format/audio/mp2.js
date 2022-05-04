import {Format} from "../../Format.js";

export class mp2 extends Format
{
	name           = "MPEG ADTS Layer II";
	ext            = [".mp2"];
	forbidExtMatch = true;
	magic          = ["MPEG ADTS, layer II", /^fmt\/198( |$)/];
	metaProvider   = ["soxi"];
	converters     = ["ffmpeg[outType:mp3]"];
}
