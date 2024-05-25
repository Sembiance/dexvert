import {Format} from "../../Format.js";

export class pcFile extends Format
{
	name           = "PC-File";
	website        = "http://fileformats.archiveteam.org/wiki/PC-FILE";
	ext            = [".dbf", ".rep"];
	forbidExtMatch = true;
	magic          = ["PC-File data", "PC-File Report", "PC-File mail-merge Letter"];
	notes          = "Was a somewhat used database program back in the day. Didn't really dig into what converters might be possible.";
	converters     = ["strings"];
}
