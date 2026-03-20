import {Format} from "../../Format.js";

export class trainzGameArchive extends Format
{
	name           = "Pathologic VFS Archive";
	ext            = [".ja"];
	forbidExtMatch = true;
	magic          = [/^geArchive: JA_ARCHINFO(_2)?( |$)/];
	converters     = ["gameextractor[codes:JA_ARCHINFO_2,JA_ARCHINFO]"];
}
