import {Format} from "../../Format.js";

export class telemateCompiledScript extends Format
{
	name           = "Telemate Compiled Script";
	ext            = [".tms"];
	forbidExtMatch = true;
	magic          = ["Telemate compiled script"];
	converters     = ["strings"];
}
