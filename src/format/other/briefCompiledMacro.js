import {Format} from "../../Format.js";

export class briefCompiledMacro extends Format
{
	name           = "Brief Compiled Macro";
	ext            = [".cm"];
	forbidExtMatch = true;
	magic          = ["Brief Compiled Macro"];
	converters     = ["strings"];
}
