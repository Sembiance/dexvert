import {Format} from "../../Format.js";

export class dbf extends Format
{
	name           = "dBase/FoxBase/XBase/FoxPro Database File";
	website        = "http://fileformats.archiveteam.org/wiki/DBF";
	ext            = [".dbf", ".frx", ".dbt", ".db$"];
	forbidExtMatch = true;
	magic          = [
		/^(?:FoxBase\+?\/?)?dBase .*DBF/, "dBASE Database", /^(dBase|xBase) .*DBF/, "Table MS Visual FoxPro", "FoxPro with memo DBF", "Visual FoxPro", "dBase Datendatei", "Form MS Visual FoxPro 7", "FoxPro Screen (generic)", "FoxPro Project (generic)",
		"FoxPro Menu (generic)",
		/^dBase I[IV]I? DBT/, /^x-fmt\/(9|271)( |$)/, /^fmt\/(373|374|376|377|379|380|381)( |$)/
	];
	forbiddenMagic = [/^(dBase|xBase) .*DBF, no records/];
	idMeta         = ({macFileType, macFileCreator}) => (["F+DB", "F+FR", "F+LB", "F+RP", "FDBC", "FMNX", "FPJX", "FSCX"].includes(macFileType) && ["FOX+", "FOXX"].includes(macFileCreator)) ||
		([".DBF", ".Dxx", "DBF ", "dDBF"].includes(macFileType) && ["ACT!", "dBAS", "FILL"].includes(macFileCreator));
	converters     = ["soffice[format:dBase]", "excel97[strongMatch]", "strings[strongMatch][hasExtMatch]"];
}
