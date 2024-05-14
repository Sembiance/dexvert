import {Format} from "../../Format.js";

export class voc extends Format
{
	name         = "Creative Voice";
	website      = "http://fileformats.archiveteam.org/wiki/Creative_Voice_File";
	ext          = [".voc"];
	magic        = ["Creative Voice audio", "Creative Labs voice data", "Creative Voice", /^fmt\/1736( |$)/];
	idMeta       = ({macFileType}) => macFileType==="VOC ";
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[format:voc][outType:mp3]"];
}
