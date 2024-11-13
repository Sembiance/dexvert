import {Format} from "../../Format.js";

export class musepack extends Format
{
	name         = "Musepack Audio";
	website      = "http://justsolve.archiveteam.org/wiki/Musepack_Audio";
	ext          = [".mpc", ".mp+", ".mpp"];
	magic        = ["Musepack encoded audio", "audio/x-musepack", "Musepack (mpc)", "MP+ SV7.0 Musikdatei", "MP+ SV0.0 Musikdate",  /^Musepack audio/];
	converters   = ["ffmpeg[format:mpc][outType:mp3]"];
}
