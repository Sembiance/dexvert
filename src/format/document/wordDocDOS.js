import {Format} from "../../Format.js";

export class wordDocDOS extends Format
{
	name           = "Microsoft Word for DOS Document";
	ext            = [".doc", ".dcx"];
	forbidExtMatch = true;
	magic          = ["Microsoft Word for DOS Document", /^Microsoft Word [\d.-]+ (DOS)/, /^Microsoft Word f.r DOS\/Write Dokument/, /^x-fmt\/274( |$)/];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["softwareBridge[format:word5]", "softwareBridge[format:word]", "strings"];
}
