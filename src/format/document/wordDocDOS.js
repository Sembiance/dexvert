import {Format} from "../../Format.js";

export class wordDocDOS extends Format
{
	name           = "Microsoft Word for DOS Document";
	ext            = [".doc", ".dcx"];
	forbidExtMatch = true;
	magic          = ["Microsoft Word for DOS Document", /^Microsoft Word f.r DOS\/Write Dokument/];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["strings"];
}
