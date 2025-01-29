import {Format} from "../../Format.js";

export class speex extends Format
{
	name           = "Speex Encoded Audio";
	website        = "http://fileformats.archiveteam.org/wiki/Speex";
	ext            = [".spx"];
	forbidExtMatch = [".spx"];
	magic          = ["Speex encoded audio", "audio/x-speex+ogg", /^Ogg data, Speex audio/, /^fmt\/948( |$)/];
	converters     = ["ffmpeg[format:ogg][outType:mp3]"];
}
