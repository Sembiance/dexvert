import {Format} from "../../Format.js";

export class au extends Format
{
	name         = "Sun Microsystems Audio File";
	website      = "http://fileformats.archiveteam.org/wiki/AU";
	ext          = [".au", ".snd"];
	magic        = ["NeXT/Sun sound", "Sun/NeXT audio data", "NeXT/Sun uLaw/AUdio format", "SUN Musik Datei", "AU audio data", /^x-fmt\/139( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="ULAW" && macFileCreator==="TVOD";
	mimeType     = "audio/basic";
	metaProvider = ["soxi"];
	converters   = ["ffmpeg[outType:mp3]", "sox"];
}
