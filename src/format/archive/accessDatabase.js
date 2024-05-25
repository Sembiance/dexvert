import {Format} from "../../Format.js";

export class accessDatabase extends Format
{
	name       = "Microsoft Access Database";
	website    = "http://fileformats.archiveteam.org/wiki/Access";
	ext        = [".mdb", ".mde", ".accdb", ".accde"];
	magic      = ["Microsoft Access Database", "Microsoft Jet DB", "Microsoft Access 2007 Database", "Microsoft Access Datenbank Datei", "Format: Microsoft Access database", /^fmt\/(275|1806|1258)( |$)/, /^x-fmt\/(66|238|239|240|241)( |$)/];
	converters = ["unmdb", "msAccess95 -> unmdb"];
}
