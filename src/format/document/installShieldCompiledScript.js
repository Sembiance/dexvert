import {Format} from "../../Format.js";

export class installShieldCompiledScript extends Format
{
	name        = "InstallShield Compiled Script";
	ext         = [".inx"];
	magic       = ["InstallShield Compiled Rules", /^fmt\/197( |$)/];
	unsupported = true;	// decompile with SID does work, but 95% of the output is useless boilerplate content
	//converters = ["SID"];
}
