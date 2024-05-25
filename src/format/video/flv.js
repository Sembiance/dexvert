import {Format} from "../../Format.js";

export class flv extends Format
{
	name         = "Flash Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLV";
	ext          = [".flv"];
	magic        = ["Macromedia Flash Video", "Flash Video", "Format: Flash Video", /^x-fmt\/382( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
