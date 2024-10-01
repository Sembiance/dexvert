import {Format} from "../../Format.js";

export class mka extends Format
{
	name             = "Matroska Audio";
	website          = "http://fileformats.archiveteam.org/wiki/Matroska_Audio";
	ext              = [".mka"];
	magic            = ["Matroska Video stream", "Matroska data", "EBML file, creator matroska", "Extensible Binary Meta Language / Matroska stream", "application/x-matroska", "Matroska / WebM (matroska,webm)", /^fmt\/569( |$)/];
	confidenceAdjust = () => -10;	// Reduce by 10 so that mkv matches first
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]"];
}
