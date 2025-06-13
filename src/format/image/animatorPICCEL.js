import {Format} from "../../Format.js";

export class animatorPICCEL extends Format
{
	name           = "Animator PIC/CEL";
	website        = "http://fileformats.archiveteam.org/wiki/Animator_PIC/CEL";
	ext            = [".cel", ".pic"];
	forbidExtMatch = true;
	magic          = [/^x-fmt\/223( |$)/];
	converters     = ["wuimg", "imageAlchemy"];
}
