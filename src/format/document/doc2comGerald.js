import {Format} from "../../Format.js";

export class doc2comGerald extends Format
{
	name           = "DOC2COM (Gerald DePyper)";
	website        = "http://fileformats.archiveteam.org/wiki/DOC2COM_(Gerald_DePyper)";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["DOC2COM (Gerald DePyper)"];
	converters     = ["deark[module:doc2com]"];
}
