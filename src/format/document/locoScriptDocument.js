import {Format} from "../../Format.js";

export class locoScriptDocument extends Format
{
	name           = "LocoScript Document";
	website        = "http://justsolve.archiveteam.org/wiki/LocoScript";
	ext            = [".000", ".a00"];
	forbidExtMatch = true;
	magic          = [/^LocoScript \d document/, "LocoScript PCW document", /^fmt\/(1304|1305)( |$)/];
	converters     = ["ailink"];
}
