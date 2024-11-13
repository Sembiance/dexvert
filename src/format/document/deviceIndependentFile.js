import {Format} from "../../Format.js";

export class deviceIndependentFile extends Format
{
	name           = "Device Independent File";
	website        = "http://fileformats.archiveteam.org/wiki/DVI_(Device_Independent_File_Format)";
	ext            = [".dvi"];
	forbidExtMatch = true;
	magic          = ["TeX DVI file", "Device Independent Document", "DVI Datei (TeX)", "Format: Device Independent Document", "application/x-dvi", /^fmt\/160( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="ODVI" && macFileCreator==="OTEX") || (macFileType==="Dvi+" && macFileCreator==="TeX+");
	converters     = ["dvi2pdf"];
	metaProvider   = ["dviinfox"];
}
