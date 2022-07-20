import {Format} from "../../Format.js";

export class dbf extends Format
{
	name           = "dBase/FoxBase/XBase Database File";
	website        = "http://fileformats.archiveteam.org/wiki/DBF";
	ext            = [".dbf", ".frx", ".dbt"];
	forbidExtMatch = true;
	magic          = [/^(?:FoxBase\+?\/?)?dBase .*DBF/, "dBASE Database", /^xBase .*DBF/, "Table MS Visual FoxPro", "FoxPro with memo DBF", /^dBase I[IV]I? DBT/, /^x-fmt\/9( |$)/, /^fmt\/373( |$)/];
	weakMagic      = [/^dBase I[IV]I? DBT/];
	converters     = ["soffice", "strings"];
}
