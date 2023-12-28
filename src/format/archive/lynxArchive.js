import {Format} from "../../Format.js";

export class lynxArchive extends Format
{
	name           = "LyNX Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Lynx_archive";
	ext            = [".lnx"];
	forbidExtMatch = true;
	magic          = ["Lynx archive", "LyNX archive"];
	converters     = ["DirMaster"];
}
