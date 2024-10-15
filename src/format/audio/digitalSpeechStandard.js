import {Format} from "../../Format.js";

export class digitalSpeechStandard extends Format
{
	name       = "Digital Speech Standard";
	website    = "http://justsolve.archiveteam.org/wiki/Digital_Speech_Standard";
	ext        = [".dss"];
	magic      = ["Digital Speech Standard audio", "Digital Speech Standard (DSS) (dss)", /^fmt\/1007( |$)/];
	converters = ["ffmpeg[format:dss][outType:mp3]"];
}
