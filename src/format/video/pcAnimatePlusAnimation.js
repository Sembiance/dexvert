import {Format} from "../../Format.js";

export class pcAnimatePlusAnimation extends Format
{
	name           = "PC Animate Plus Animation";
	ext            = [".bin", ".ani"];
	forbidExtMatch = true;
	magic          = ["PC Animate Plus Animation", "PC Animate Plus Animation File"];
	converters     = ["na_eofdec[format:pcanimplus]"];
}
