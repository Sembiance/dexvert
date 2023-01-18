import {Format} from "../../Format.js";

export class winampCompiledMakiScript extends Format
{
	name           = "Winamp Compiled Maki Script";
	ext            = [".maki"];
	forbidExtMatch = true;
	magic          = ["Compiled Winamp Maki script"];
	converters     = ["makiDecompiler"];
}
