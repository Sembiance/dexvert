import {Format} from "../../Format.js";

export class deluxePrint extends Format
{
	name           = "Deluxe Print Document/Project";
	ext            = [".bnr2", ".lbl2", ".lhd2", ".sgn2", ".bnnr", ".labl", ".lthd", ".sign"];
	forbidExtMatch = true;
	magic          = ["Deluxe Print"];
	converters     = ["strings"];
}
