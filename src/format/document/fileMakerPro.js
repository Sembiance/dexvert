import {Format} from "../../Format.js";

export class fileMakerPro extends Format
{
	name           = "FileMaker Pro Database";
	website        = "http://fileformats.archiveteam.org/wiki/FileMaker_Pro";
	ext            = [".fp3"];
	forbidExtMatch = true;
	magic          = ["FileMaker Pro 3 database", "Filemaker Pro (generic)", "FileMaker Pro database", /^x-fmt\/(318|319)( |$)/, /^fmt\/(194|1059|1072|1237)( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["FMP3", "FMP5"].includes(macFileType) ||
		(macFileType==="FMPR" && ["FMPR", "FMPU"].includes(macFileCreator)) ||
		(macFileType==="FMKD" && macFileCreator==="FMKR") ||
		(macFileType==="FMPJ" && macFileCreator==="FMPJ") ||
		(macFileType==="FMK$" && macFileCreator==="FMK4");
	converters     = ["strings"];
}
