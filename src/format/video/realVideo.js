import {Format} from "../../Format.js";

export class realVideo extends Format
{
	name         = "RealVideo";
	website      = "http://fileformats.archiveteam.org/wiki/RealMedia";
	ext          = [".rm", ".rv", ".rmvb", ".rmf"];
	magic        = [/^RealMedia [Ff]ile/, "Real Media stream", "RealVideo", /^x-fmt\/190( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
