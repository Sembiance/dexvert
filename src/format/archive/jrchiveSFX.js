import {Format} from "../../Format.js";

export class jrchiveSFX extends Format
{
	name           = "JRchive Self-Extracting Archive";
	website        = "http://justsolve.archiveteam.org/wiki/JRchive";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["overlay: JRchive SFX", /^idarc: JRC( |$)/];
	converters     = ["dosEXEExtract"];
}
