import {Format} from "../../Format.js";

export class installShieldCompiledScript extends Format
{
	name       = "InstallShield Compiled Script";
	ext        = [".inx"];
	magic      = ["InstallShield Compiled Rules", /^fmt\/197( |$)/];
	converters = ["SID"];
}
