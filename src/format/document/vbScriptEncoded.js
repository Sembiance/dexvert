import {Format} from "../../Format.js";

export class vbScriptEncoded extends Format
{
	name           = "VBScript Encoded script";
	ext            = [".vbe"];
	forbidExtMatch = true;
	magic          = ["VBScript Encoded script", "Windows Script Encoded Data", "text/jscript.encode"];
	converters     = ["vbeDecoder"];
}
