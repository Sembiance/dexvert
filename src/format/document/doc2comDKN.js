import {Format} from "../../Format.js";

export class doc2comDKN extends Format
{
	name           = "DOC2COM (Dan K. Nelson)";
	website        = "http://fileformats.archiveteam.org/wiki/DOC2COM_(Dan_K._Nelson)";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["DOC2COM (Dan K. Nelson)", "deark: doc2com_dkn"];
	converters     = ["deark[module:doc2com_dkn][opt:text:encconv=0]"];
}
