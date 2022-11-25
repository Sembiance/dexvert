import {Format} from "../../Format.js";

export class installShieldCompiledScript extends Format
{
	name        = "InstallShield Compiled Script";
	ext         = [".inx"];
	magic       = ["InstallShield Compiled Rules", /^fmt\/197( |$)/];
	unsupported = true;
	notes       = "We used to decompile this using SID, but it produces nearly useless boilerplate content";
	//converters = ["SID"];
}
