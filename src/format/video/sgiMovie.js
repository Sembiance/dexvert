import {Format} from "../../Format.js";

export class sgiMovie extends Format
{
	name           = "Silicon Graphics IRIX Movie";
	website        = "http://fileformats.archiveteam.org/wiki/SGI_movie";
	ext            = [".mv", ".movie", ".sgi"];
	forbidExtMatch = [".movie"];
	magic          = ["SGI video", "Silicon Graphics movie file", "video/x-sgi-movie", "Silicon Graphics Movie (mv)", /^fmt\/1901( |$)/];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg[format:mv]", "xanim"];
}
