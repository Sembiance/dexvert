import {Format} from "../../Format.js";

export class lotus123 extends Format
{
	name           = "Lotus 1-2-3 File";
	website        = "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3";
	ext            = [".wks", ".wk1", ".wk2", ".wk3", ".wk4", ".wk5", ".123", ".wkb", ".wrk", ".dbs", ".wr1"];
	forbidExtMatch = [".dbs", ".wrk"];
	magic          = [
		"Lotus 123 Worksheet", /^Lotus 1-2-3 (unknown )?[Ww]or[Kk][Ss]heet/, "Lotus 1-2-3/Symphony worksheet", "Lotus 123/Symphony worksheet", "Lotus Symphony Worksheet", "Lotus unknown worksheet", "application/vnd.lotus-1-2-3", /^Lotus Symphony WoRksheet/,
		/^fmt\/(1452|1453)( |$)/, /^x-fmt\/(114|115|116|117)( |$)/
	];
	weakMagic  = ["Lotus 123/Symphony worksheet/format/configuration (V1-V2)"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="LWKS" && ["L123", "XCEL"].includes(macFileCreator);
	converters = ["soffice[format:Lotus]", "excel97[hasExtMatch][matchType:magic]", "soffice[hasExtMatch][matchType:magic]"];
}
