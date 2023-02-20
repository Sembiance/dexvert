import {Format} from "../../Format.js";

export class funComISSAudio extends Format
{
	name           = "FunCom ISS Audio";
	website        = "http://fileformats.archiveteam.org/wiki/Funcom_ISS";
	ext            = [".iss"];
	forbidExtMatch = true;
	magic          = ["FunCom ISS audio"];
	converters     = ["ffmpeg[outType:mp3]"];
}
