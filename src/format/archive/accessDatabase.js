import {Format} from "../../Format.js";

export class accessDatabase extends Format
{
	name       = "Microsoft Access Database";
	website    = "http://fileformats.archiveteam.org/wiki/Access";
	ext        = [".mdb", ".mde", ".accdb", ".accde"];
	magic      = ["Microsoft Access Database", "Microsoft Jet DB", "Microsoft Access 2007 Database", /^fmt\/(275|1258)( |$)/, /^x-fmt\/(66|238|239|241)( |$)/];
	converters = ["unmdb"];
}
