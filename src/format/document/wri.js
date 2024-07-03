import {Format} from "../../Format.js";

export class wri extends Format
{
	name           = "Windows Write Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Write";
	ext            = [".wri", ".wr", ".doc"];
	weakExt        = [".doc"];
	forbidExtMatch = true;
	magic          = ["Windows Write Document", /^Microsoft Write.* Document/, "Write for Windows Document", "Format: Windows Write document", /^x-fmt\/(4|12)( |$)/];
	weakMagic      = ["Windows Write Document", "Format: Windows Write document"];
	converters     = ["soffice[format:MS Write]", "fileMerlin[type:MSWR]", "keyViewPro[outType:pdf]", "word97"];
}
