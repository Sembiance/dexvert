import {Format} from "../../Format.js";

export class folioInfobase extends Format
{
	name           = "Folio Infobase";
	website        = "http://fileformats.archiveteam.org/wiki/Folio_Infobase";
	ext            = [".nfo", ".sdw", ".fff", ".def"];
	forbidExtMatch = true;
	magic          = ["Infobase (Folio)", "Folio Infobase", /^fmt\/(1157|1158|1159|1160|1161|1162|1163)( |$)/];
	converters     = ["vibeExtract"];
}
