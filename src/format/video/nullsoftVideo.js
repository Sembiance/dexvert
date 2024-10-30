import {Format} from "../../Format.js";

export class nullsoftVideo extends Format
{
	name         = "Nullsoft Video";
	website      = "https://wiki.multimedia.cx/index.php/Nullsoft_Video";
	ext          = [".nsv"];
	magic        = ["Nullsoft Video", "Nullsoft Streaming Video", "video/x-nsv", "Nullsoft Streaming Video (nsv)", /^fmt\/1176( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:nsv]"];
}
