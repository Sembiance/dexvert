import {Format} from "../../Format.js";

export class wordDocDOS extends Format
{
	name           = "Microsoft Word for DOS Document";
	ext            = [".doc", ".dcx"];
	forbidExtMatch = true;
	magic          = ["Microsoft Word for DOS Document"];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["strings"];
}
