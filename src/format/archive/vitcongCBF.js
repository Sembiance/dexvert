import {Format} from "../../Format.js";

export class vitcongCBF extends Format
{
	name           = "Vietcong CBF Archive";
	ext            = [".cbf"];
	forbidExtMatch = true;
	magic          = ["dragon: CBF0", "dragon: CBF1"];
	converters     = ["dragonUnpacker[types:CBF1]", "dragonUnpacker[types:CBF0]"];
}
