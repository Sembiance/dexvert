import {Format} from "../../Format.js";

export class folioDatabase extends Format
{
	name           = "Folio Database";
	website        = "http://fileformats.archiveteam.org/wiki/Folio_Infobase";
	ext            = [".nfo", ".sdw", ".fff", ".def"];
	forbidExtMatch = true;
	magic          = ["Infobase (Folio)", /^fmt\/(1157|1158|1159|1160|1161|1162|1163)( |$)/];
	unsupported    = true;
}
