import {Format} from "../../Format.js";

export class quattroPro extends Format
{
	name           = "Quattro Pro";
	website        = "http://fileformats.archiveteam.org/wiki/Quattro_Pro";
	ext            = [".wq1", ".wq2", ".wb1", ".wb2", ".wb3", ".qpw"];
	forbidExtMatch = true;
	magic          = ["Quattro Pro for Windows spreadsheet", /^fmt\/837( |$)/];
	converters     = ["soffice"];
}