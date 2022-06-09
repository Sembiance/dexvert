import {Format} from "../../Format.js";

export class mikMod extends Format
{
	name           = "MikMod Module";
	ext            = [".uni"];
	forbidExtMatch = true;
	magic          = ["MikMod module"];
	metaProvider   = ["musicInfo"];
	converters     = ["mikmod2wav"];
}
