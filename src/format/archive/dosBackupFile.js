import {Format} from "../../Format.js";

export class dosBackupFile extends Format
{
	name       = "DOS BACKUP file";
	website    = "http://fileformats.archiveteam.org/wiki/BACKUP_(MS-DOS)";
	magic      = [/^DOS 2\.0-3\.2 backed up file/, "DOS 2.0-3.2 backup"];
	converters = ["unDOSBACKUP"];
}
