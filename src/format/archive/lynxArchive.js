import {Format} from "../../Format.js";

export class lynxArchive extends Format
{
	name           = "LyNX Archive";
	ext            = [".lnx"];
	forbidExtMatch = true;
	magic          = ["Lynx archive", "LyNX archive"];
	converters     = ["DirMaster"];
}
