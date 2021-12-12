import {Format} from "../../Format.js";

export class installShieldCompiledScript extends Format
{
	name       = "InstallShield Compiled Script";
	ext        = [".inx"];
	magic      = ["InstallShield Compiled Rules"];
	converters = ["SID"];
}
