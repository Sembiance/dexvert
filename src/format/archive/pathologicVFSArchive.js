import {Format} from "../../Format.js";

export class pathologicVFSArchive extends Format
{
	name           = "Pathologic VFS Archive";
	ext            = [".vfs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: VFS_LP1C( |$)/];
	converters     = ["gameextractor[codes:VFS_LP1C]"];
}
