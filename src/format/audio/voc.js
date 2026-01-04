import {Format} from "../../Format.js";

export class voc extends Format
{
	name         = "Creative Voice";
	website      = "http://fileformats.archiveteam.org/wiki/Creative_Voice_File";
	ext          = [".voc"];
	magic        = ["Creative Voice audio", "Creative Labs voice data", "Creative Voice", /^soxi: voc$/, /^fmt\/1736( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="VOC " || (macFileType==="ovc " && macFileCreator==="BSnd");
	metaProvider = ["soxi"];
	converters   = ["sox[type:voc]", "ffmpeg[format:voc][outType:mp3]"];
}
