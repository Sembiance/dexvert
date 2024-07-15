import {Format} from "../../Format.js";

export class macOSFont extends Format
{
	name           = "MacOS X Font";
	ext            = [".fnt", ".wfn"];
	forbidExtMatch = true;
	magic          = [/^fmt\/660( |$)/];
	converters     = ["fontforge"];
}
