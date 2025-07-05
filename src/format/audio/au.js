import {Format} from "../../Format.js";

export class au extends Format
{
	name           = "Sun Microsystems Audio File";
	website        = "http://fileformats.archiveteam.org/wiki/AU";
	ext            = [".au", ".snd"];
	forbidExtMatch = [".snd"];
	magic          = ["NeXT/Sun sound", "Sun/NeXT audio data", "NeXT/Sun uLaw/AUdio format", "SUN Musik Datei", "AU audio data", "audio/basic", "Sun AU (au)", /^soxi: au$/, /^x-fmt\/139( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="ULAW" || (macFileType==="NxTS" && macFileCreator==="SDHK");
	mimeType       = "audio/basic";
	metaProvider   = ["soxi"];
	converters     = ["ffmpeg[format:au][outType:mp3]", "sox[matchType:magic]"];
}
