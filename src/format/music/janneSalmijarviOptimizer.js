import {xu} from "xu";
import {Format} from "../../Format.js";

export class janneSalmijarviOptimizer extends Format
{
	name         = "Janne Salmijarvi Optimizer";
	ext          = [".js"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Janne_Salmijarvi_Optimizer]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
