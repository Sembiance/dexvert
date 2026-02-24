import {Format} from "../../Format.js";

export class maxisGameDataArchive extends Format
{
	name           = "Maxis game data archive";
	ext            = [".package"];
	forbidExtMatch = true;
	magic          = ["Maxis game data archive", /^Maxis Database Packed File/, /^geArchive: (DAT_DBPF|PACKAGE_DBPF_2|PACKAGE_DBPF)( |$)/];
	converters     = ["gameextractor[codes:DAT_DBPF,PACKAGE_DBPF_2,PACKAGE_DBPF]"];
}
