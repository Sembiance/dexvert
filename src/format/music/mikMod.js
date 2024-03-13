import {Format} from "../../Format.js";

export class mikMod extends Format
{
	name           = "MikMod Module";
	ext            = [".uni"];
	forbidExtMatch = true;
	magic          = ["MikMod module", "MikMod UNI format module sound data"];
	metaProvider   = ["musicInfo"];
	converters     = ["mikmod2wav"];
}
