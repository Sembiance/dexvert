import {Format} from "../../Format.js";

export class dbf extends Format
{
	name           = "dBase/FoxBase/XBase/FoxPro Database File";
	website        = "http://fileformats.archiveteam.org/wiki/DBF";
	ext            = [".dbf", ".frx", ".dbt", ".db$"];
	forbidExtMatch = true;
	magic          = [
		/^(?:FoxBase\+?\/?)?dBase .*DBF/, "dBASE Database", /^(dBase|xBase) .*DBF/, "Table MS Visual FoxPro", "FoxPro with memo DBF", "Visual FoxPro", "dBase Datendatei", "Form MS Visual FoxPro 7",
		/^dBase I[IV]I? DBT/, /^x-fmt\/(9|271)( |$)/, /^fmt\/(373|374|376|377|379|380|381)( |$)/
	];
	forbiddenMagic = [/^(dBase|xBase) .*DBF, no records/];
	weakMagic      = [/^dBase I[IV]I? DBT/, "Visual FoxPro"];
	converters     = ["soffice[format:dBase]", "excel97[strongMatch]", "strings[strongMatch]"];
}
