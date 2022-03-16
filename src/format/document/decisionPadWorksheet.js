import {Format} from "../../Format.js";

export class decisionPadWorksheet extends Format
{
	name           = "Decision Pad Worksheet";
	ext            = [".dpw"];
	forbidExtMatch = true;
	magic          = ["Decision Pad Worksheet"];
	converters     = ["strings"];
}
