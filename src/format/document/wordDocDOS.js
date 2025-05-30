import {Format} from "../../Format.js";

export class wordDocDOS extends Format
{
	name           = "Microsoft Word for DOS Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Word";
	ext            = [".doc", ".dcx"];
	forbidExtMatch = true;
	magic          = ["Microsoft Word for DOS Document", /^Microsoft Word [\d.-]+ \(DOS\)/, /^Microsoft Word f.r DOS\/Write Dokument/, /^fmt\/1688( |$)/, /^x-fmt\/(274|275|276)( |$)/];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["softwareBridge[format:word5]", "softwareBridge[format:word]", "wordForWord", "strings"];
}
