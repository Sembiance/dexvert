import {Format} from "../../Format.js";

export class flv extends Format
{
	name         = "Flash Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLV";
	ext          = [".flv"];
	magic        = ["Macromedia Flash Video", "Flash Video", "Format: Flash Video", "video/x-flv", "FLV (Flash Video) (flv)", /^x-fmt\/382( |$)/];
	idMeta       = ({macFileType}) => macFileType==="MFLV";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flv]"];
}
