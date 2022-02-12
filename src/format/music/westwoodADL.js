import {Format} from "../../Format.js";

export class westwoodADL extends Format
{
	name         = "Westwood ADL";
	ext          = [".adl"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
