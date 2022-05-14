import {Format} from "../../Format.js";

export class wri extends Format
{
	name           = "Windows Write Document";
	website        = "http://fileformats.archiveteam.org/wiki/WRI";
	ext            = [".wri", ".wr", ".doc"];
	forbidExtMatch = true;
	magic          = ["Windows Write Document", /^Microsoft Write.* Document/, "Write for Windows Document", /^x-fmt\/12( |$)/];
	converters     = ["soffice", "fileMerlin[type:MSWR]", "word97"];
}
