import {Format} from "../../Format.js";

export class dbf extends Format
{
	name           = "dBase/FoxBase/XBase Database File";
	website        = "http://fileformats.archiveteam.org/wiki/DBF";
	ext            = [".dbf", ".frx"];
	forbidExtMatch = true;
	magic          = [/^(?:FoxBase\+?\/?)?dBase .*DBF/, "dBASE Database", /^xBase .*DBF/, "Table MS Visual FoxPro", "FoxPro with memo DBF"];
	converters     = ["soffice[outType:csv]", "strings"];
}
