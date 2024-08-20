import {Format} from "../../Format.js";

export class abiWord extends Format
{
	name           = "AbiWord Document";
	website        = "http://fileformats.archiveteam.org/wiki/AbiWord";
	ext            = [".abw", ".zabw", ".doc"];
	forbidExtMatch = true;
	magic          = ["AbiWord document", /^fmt\/(890|891)( |$)/];
	converters     = ["soffice"];
}
