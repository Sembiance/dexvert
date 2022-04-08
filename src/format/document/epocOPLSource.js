import {Format} from "../../Format.js";

export class epocOPLSource extends Format
{
	name           = "EPOC OPL Source";
	ext            = [".opl"];
	forbidExtMatch = true;
	magic          = ["EPOC OPL source", "Psion Series 5 OPL program"];
	converters     = ["psiconv[outType:ASCII]"];
}
